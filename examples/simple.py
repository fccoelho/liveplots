"""Simple example: basic PlotServer usage."""

import time

from numpy import random

from liveplots import PlotServer

ps = PlotServer(port=0, persist=1)

data1 = random.normal(0, 1, 1000).tolist()
data2 = random.normal(4, 1, 1000).tolist()
ps.lines([data1, data2], [], ["N(0,1)", "N(4,1)"], "Two Gaussians")
ps.flush_queue()

print("Lines plotted. Sending 20 histogram updates...")

t0 = time.perf_counter()
for n in range(20):
    d = random.normal(n * 0.3, 1, 200)
    ps.histogram(d.tolist(), ["data"], f"Step {n}")
    ps.flush_queue()
    time.sleep(0.1)
total = time.perf_counter() - t0

print(f"Animated 20 histograms in {total:.1f}s")

ps.close()
