import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import time

runtime = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
lock = (runtime / "rice-recorder.lock").open("w")

try:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    raise SystemExit(0)

def notify(title, body):
    try:
        subprocess.run(["notify-send", title, body], check=False)
    except FileNotFoundError:
        pass

# Toggle off an existing recorder belonging to this user.
running = subprocess.run(
    ["pgrep", "-u", str(os.getuid()), "-x", "wf-recorder"],
    capture_output=True, text=True,
)
if running.returncode == 0:
    for pid in running.stdout.split():
        try:
            os.kill(int(pid), signal.SIGINT)
        except ProcessLookupError:
            pass
    notify("Recording stopping", "Finishing the video in ~/Videos/Recordings")
    raise SystemExit(0)

# MangoWC: get outputs via mmsg. Fallback: wlrandr-style? try mmsg first.
output_name = None
try:
    # Prefer focused monitor info; fallbacks for API variations.
    for cmd in (["mmsg", "get", "focusing-monitor"], ["mmsg", "get", "all-monitors"]):
        try:
            out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        except Exception:
            continue
        out = out.strip()
        if not out:
            continue
        try:
            data = json.loads(out)
        except Exception:
            # Some mmsg builds may prefix text; try last JSON object/array.
            try:
                start = min([i for i in (out.find("{"), out.find("[")) if i != -1])
                data = json.loads(out[start:])
            except Exception:
                continue
        if isinstance(data, dict):
            output_name = data.get("name") or data.get("output")
            if not output_name and isinstance(data.get("monitor"), dict):
                output_name = data["monitor"].get("name")
        elif isinstance(data, list) and data:
            focused = next((m for m in data if isinstance(m, dict) and (m.get("focused") or m.get("focus"))), None)
            m = focused or (data[0] if isinstance(data[0], dict) else None)
            if m:
                output_name = m.get("name") or m.get("output")
        if output_name:
            break
except Exception:
    output_name = None

if not output_name:
    notify("Recording failed", "No focused display found (mmsg). Is MangoWC running?")
    raise SystemExit(1)

folder = Path.home() / "Videos/Recordings"
folder.mkdir(parents=True, exist_ok=True)
filename = folder / (time.strftime("%Y%m%d_%H%M%S") + f"_{time.time_ns()}.mp4")
logfile = runtime / "rice-recorder.log"

with logfile.open("w") as log:
    process = subprocess.Popen(
        ["wf-recorder", "-o", output_name, "-f", str(filename)],
        stdout=log, stderr=log, start_new_session=True,
    )

time.sleep(0.7)
if process.poll() is None:
    notify("Screen recording started", f"Output: {output_name}. Super+Shift+F9 to stop. Video only.")
else:
    notify("Recording failed", f"See {logfile}")
