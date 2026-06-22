# Tutorial

## Installation

Before using liveplots, you need Gnuplot installed on your system.

### Debian/Ubuntu

```bash
sudo apt install gnuplot
```

### macOS

```bash
brew install gnuplot
```

### Python package

```bash
uv add liveplots
```

## Basic Plotting

### Starting a server

Create a `PlotServer` — this starts a ZeroMQ server in a background thread
and connects a client with two sockets:

- **PUSH** socket for plot data (fire-and-forget, never blocks)
- **REQ** socket for control commands (synchronous)

```python
from liveplots import PlotServer

pserver = PlotServer(port=0, persist=1)
```

- `port=0` auto-selects an available port (starting from 10001)
- `persist=1` keeps the gnuplot window open after the process exits

### Line plots

```python
from numpy.random import normal

data = [normal(0, 1, 100).tolist() for _ in range(4)]
pserver.lines(data, [], ["a", "b", "c", "d"], "My Plot", "lines")
```

Parameters:

| Parameter | Description |
|-----------|-------------|
| `data`    | List of lists (one per series) |
| `x`       | X-axis values (empty list = use indices) |
| `labels`  | Legend labels for each series |
| `title`   | Plot title |
| `style`   | Gnuplot style: `lines`, `boxes`, `points`, `linespoints`, etc. |
| `multiplot` | `1` to create a grid of subplots |

### Scatter plots

```python
x = normal(0, 1, 100).tolist()
y = normal(0, 2, 100).tolist()
pserver.scatter(x, y, ["x", "y"], "Scatter Plot")
```

### Histograms

```python
data = normal(0, 1, 1000).tolist()
pserver.histogram(data, ["distribution"], "Histogram")
```

### Multiplot layouts

Pass `multiplot=1` to any plotting method to create a grid of subplots:

```python
data = [normal(i, 1, 100).tolist() for i in range(4)]
pserver.lines(data, [], ["a", "b", "c", "d"], "Multiplot", "lines", 1)
```

### Flushing the queue

Plot commands are fire-and-forget (sent via PUSH, no response expected).
To block until the server has finished processing all pending plots:

```python
pserver.flush_queue()
```

This sends a synchronous control command via REQ/REP that blocks until
the server's internal queue is drained.

## File System Monitoring

The `Monitor` class watches files/directories and triggers a callback:

```python
from liveplots import Monitor

def on_change(filepath):
    print(f"File changed: {filepath}")
    # Load and plot the data...

monitor = Monitor("/path/to/watch", ["create", "modify"], on_change)

# ... later
monitor.stop()
```

### Supported events

| Event name     | Description |
|----------------|-------------|
| `create`       | File/directory created |
| `delete`       | File/directory deleted |
| `close_write`  | Writable file closed |
| `close_nowrite`| Read-only file closed |
| `access`       | File accessed |
| `attrib`       | Metadata changed |
| `modify`       | File modified |

## Combining Monitoring + Plotting

```python
from liveplots import Monitor, PlotServer
from numpy import load

pserver = PlotServer()

def action(filepath):
    data = load(filepath)
    pserver.lines(data.tolist(), [], ["data"], "")

monitor = Monitor("/tmp", ["close_write"], action)
```

## Running Multiple Servers

Each `PlotServer` runs on its own daemon process. You can create multiple
servers to display different plots simultaneously:

```python
pserver1 = PlotServer(port=0, persist=1)
pserver2 = PlotServer(port=0, persist=1)

pserver1.lines(data1, [], ["series"], "Server 1")
pserver2.histogram(data2, ["hist"], "Server 2")
```
