"""Simple example: create plot servers and send data."""

import time

from numpy import random

from liveplots import PlotServer

data = random.normal(0, 1, 1000)
data2 = random.normal(4, 1, 1000)

pserver = PlotServer(port=0, persist=1)
pserver2 = PlotServer(port=0, persist=1)

scatter_data = [random.normal(random.randint(0, 10), 1, size=100).tolist() for _ in range(7)]
scatter_data2 = [random.normal(random.randint(0, 10), 1, size=100).tolist() for _ in range(7)]
pserver.scatter(scatter_data, scatter_data2, [], "Multiplot", "points", 0, 1)
pserver.flush_queue()

n_plots = 50
t0 = time.perf_counter()
for n in range(n_plots):
    d = random.normal(random.randint(0, 10), 1, size=100)
    d2 = random.normal(random.randint(0, 10), 1, size=100)
    pserver2.histogram([d.tolist(), d2.tolist()], ["data", "data2"], f"Histogram {n}", 1)
send_elapsed = time.perf_counter() - t0

pserver2.flush_queue()
total_elapsed = time.perf_counter() - t0

print(f"Sent {n_plots} histograms in {send_elapsed:.3f}s ({n_plots / send_elapsed:.0f} send/s)")
print(f"Total time (send + render): {total_elapsed:.3f}s ({n_plots / total_elapsed:.0f} plots/s)")

pserver.close()
pserver2.close()
