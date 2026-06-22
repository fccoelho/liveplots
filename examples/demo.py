"""Comprehensive demo of all liveplots capabilities.

A single PlotServer instance is reused across all sections so only one
gnuplot subprocess is spawned. Run with:

    uv run python examples/demo.py
"""

from __future__ import annotations

import sys
import time

import numpy as np

from liveplots import PlotServer


def demo_lines(ps: PlotServer) -> None:
    x = np.linspace(0, 4 * np.pi, 200)
    data = [np.sin(x * f).tolist() for f in [0.5, 1.0, 1.5, 2.0]]
    ps.lines(data, x.tolist(), ["0.5 Hz", "1 Hz", "1.5 Hz", "2 Hz"], "Sine Waves")
    ps.flush_queue()


def demo_scatter(ps: PlotServer) -> None:
    clusters_x = [np.random.normal(cx, 0.5, 100).tolist() for cx in [1, 4, 7]]
    clusters_y = [np.random.normal(cy, 0.5, 100).tolist() for cy in [1, 5, 2]]
    ps.scatter(clusters_x, clusters_y, ["A", "B", "C"], "Three Clusters", jitter=False)
    ps.flush_queue()


def demo_histogram(ps: PlotServer) -> None:
    d1 = np.random.normal(0, 1, 2000).tolist()
    d2 = np.random.normal(2, 0.8, 2000).tolist()
    d3 = np.random.normal(-2, 1.5, 2000).tolist()
    ps.histogram([d1, d2, d3], ["N(0,1)", "N(2,0.8)", "N(-2,1.5)"], "Three Distributions")
    ps.flush_queue()


def demo_error_bars(ps: PlotServer) -> None:
    x = np.linspace(0, 10, 30)
    y = 2 * np.sin(x) + np.random.normal(0, 0.3, 30)
    err = 0.3 + 0.2 * np.random.rand(30)
    ps.error_bars(
        x.tolist(),
        y.tolist(),
        err.tolist(),
        labels=["sensor"],
        title="Sensor Readings ± Error",
    )
    ps.flush_queue()


def demo_filled_curves(ps: PlotServer) -> None:
    x = np.linspace(0, 10, 200)
    mean = np.sin(x) * np.exp(-0.2 * x)
    lower = mean - 0.3 - 0.1 * x
    upper = mean + 0.3 + 0.1 * x
    ps.filled_curves(
        x.tolist(),
        lower.tolist(),
        upper.tolist(),
        labels=["band"],
        title="Damped Sine ± Confidence",
        fill_color="purple",
    )
    ps.flush_queue()


def demo_boxplot(ps: PlotServer) -> None:
    data = [
        np.random.normal(50, 5, 200).tolist(),
        np.random.normal(60, 10, 200).tolist(),
        np.random.normal(45, 8, 200).tolist(),
        np.random.normal(70, 3, 200).tolist(),
        np.random.normal(55, 15, 200).tolist(),
    ]
    ps.boxplot(data, labels=["Run A", "Run B", "Run C", "Run D", "Run E"], title="Benchmark Scores")
    ps.flush_queue()


def demo_heatmap(ps: PlotServer) -> None:
    x = np.linspace(-4, 4, 80)
    y = np.linspace(-4, 4, 80)
    xx, yy = np.meshgrid(x, y, indexing="ij")
    matrix = np.exp(-((xx - 1) ** 2 + yy**2) / 2) + 0.5 * np.exp(
        -((xx + 2) ** 2 + (yy - 1) ** 2) / 1.0
    )
    ps.heatmap(matrix.tolist(), title="Two Gaussian Bumps", colormap="hot")
    ps.flush_queue()


def demo_steps(ps: PlotServer) -> None:
    data = np.cumsum(np.random.choice([-1, 1], size=50)).astype(float).tolist()
    ps.lines([data], None, ["random walk"], "Discrete Random Walk", "fsteps")
    ps.flush_queue()


def demo_multiplot(ps: PlotServer) -> None:
    data = [
        np.sin(np.linspace(0, f * 4 * np.pi, 100) + p).tolist()
        for f, p in zip([1, 2, 3, 4, 0.5, 1.5], [0, 1, 2, 3, 4, 5], strict=True)
    ]
    ps.lines(data, None, [f"ch{i}" for i in range(6)], "6-Channel Signal", "lines", 1)
    ps.flush_queue()


def demo_realtime_stream(ps: PlotServer) -> None:
    window = 100
    data = np.zeros(window)
    print("   Streaming 30 updates...", end="", flush=True)
    for i in range(30):
        data = np.roll(data, -1)
        data[-1] = np.sin(i * 0.2) + np.random.normal(0, 0.1)
        ps.lines([data.tolist()], None, ["live"], f"Frame {i}", "lines")
        time.sleep(0.05)
    ps.flush_queue()
    print(" done.")


DEMOS = [
    ("Line Plot — multiple series", demo_lines),
    ("Scatter Plot — clusters", demo_scatter),
    ("Histogram — distributions", demo_histogram),
    ("Error Bars — measurement uncertainty", demo_error_bars),
    ("Filled Curves — confidence band", demo_filled_curves),
    ("Boxplot — distribution comparison", demo_boxplot),
    ("Heatmap — 2D field", demo_heatmap),
    ("Step Plot — discrete signal", demo_steps),
    ("Multiplot — panel layout", demo_multiplot),
    ("Real-Time Stream — live updates", demo_realtime_stream),
]


def main() -> None:
    print("liveplots Demo — all plot types in a single gnuplot window\n")
    print("Press Enter to advance, Ctrl+C to quit.\n")

    ps = PlotServer(persist=1)
    try:
        for title, fn in DEMOS:
            print(f"  {title}")
            try:
                fn(ps)
            except Exception:
                print(f"    (error in {fn.__name__})")
            try:
                input()
            except KeyboardInterrupt:
                print("\nExiting.")
                break
    finally:
        ps.close()

    print("Done.")


if __name__ == "__main__":
    sys.exit(main())
