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
    time.sleep(0.02)
send_time = time.perf_counter() - t0

ps.flush_queue()
total = time.perf_counter() - t0

print(f"Sent 20 histograms in {send_time:.3f}s")
print(f"Total (send + render): {total:.3f}s")

ps.close()
