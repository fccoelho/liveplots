"""Simple example: create plot servers and send data."""

import time

from numpy import random

from liveplots import PlotServer

# Generate sample data
data = random.normal(0, 1, 1000)
data2 = random.normal(4, 1, 1000)

# Set up a couple of servers
pserver = PlotServer(port=0, persist=1)
pserver2 = PlotServer(port=0, persist=1)

# Multiplot scatter
scatter_data = [random.normal(random.randint(0, 10), 1, size=100).tolist() for _ in range(7)]
scatter_data2 = [random.normal(random.randint(0, 10), 1, size=100).tolist() for _ in range(7)]
pserver.scatter(scatter_data, scatter_data2, [], "Multiplot", "points", 0, 1)
pserver.flush_queue()

# Succession of 500 multiplot histograms
t0 = time.time()
for n in range(500):
    d = random.normal(random.randint(0, 10), 1, size=100)
    d2 = random.normal(random.randint(0, 10), 1, size=100)
    pserver2.histogram([d.tolist(), d2.tolist()], ["data", "data2"], f"Histogram {n}", 1)
print(f"Plot rate: {500 / (time.time() - t0):.1f} plots per second")

# Wait for the queue to empty
pserver2.flush_queue()
