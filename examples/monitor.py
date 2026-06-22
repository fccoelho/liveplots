"""File monitor example: watch a directory and plot data on change."""

import time

import numpy as np

from liveplots import Monitor, PlotServer

pserver = PlotServer()


def action(fpath: str) -> None:
    """Load a .npy file and plot its contents."""
    print(f"Action triggered: {fpath}")
    if not fpath.endswith(".npy"):
        return
    try:
        data = np.load(fpath)
    except (FileNotFoundError, ValueError) as e:
        print(f"  Skipping {fpath}: {e}")
        return
    pserver.lines(data.tolist(), [], ["data"], "")


# Monitor /tmp for new files
monitor = Monitor("/tmp", ["close_write"], action, debug=True)

# Create a test file to trigger the monitor
data = np.random.normal(0, 1, 1000)
np.save("/tmp/liveplots_demo.npy", data)

# Wait for the event to be processed
time.sleep(1)
monitor.stop()
