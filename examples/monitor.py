"""File monitor example: watch a directory and plot data on change."""

import time
from pathlib import Path

import numpy as np

from liveplots import Monitor, PlotServer

watch_dir = Path("/tmp/liveplots_monitor")
watch_dir.mkdir(exist_ok=True)

pserver = PlotServer(persist=1)


def action(fpath: str) -> None:
    """Load a .npy file and plot its contents."""
    if not fpath.endswith(".npy"):
        return
    try:
        data = np.load(fpath)
    except (FileNotFoundError, ValueError) as e:
        print(f"  Skipping {fpath}: {e}")
        return
    print(f"  Plotting {fpath} ({len(data)} points)")
    pserver.lines(data.tolist(), [], ["data"], f"{Path(fpath).name}")


monitor = Monitor(str(watch_dir), ["close_write"], action, debug=True)

print(f"Monitoring {watch_dir} for .npy files...")
print("Writing 3 sample files...")

for i in range(3):
    data = np.random.normal(i, 1, 500)
    fpath = watch_dir / f"sample_{i}.npy"
    np.save(fpath, data)
    time.sleep(0.3)

time.sleep(0.5)
monitor.stop()
pserver.flush_queue()
pserver.close()
print("Done.")
