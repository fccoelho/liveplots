"""Comprehensive demo of all liveplots capabilities.

Each section creates its own plot server (own gnuplot window) and
demonstrates a different plot type. Run with:

    uv run python examples/demo.py
"""

from __future__ import annotations

import time

import numpy as np

from liveplots import PlotServer


def section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


def demo_lines() -> None:
    """Multiple overlapping line series."""
    section("1. Line Plot — multiple series")
    ps = PlotServer(persist=1)
    x = np.linspace(0, 4 * np.pi, 200)
    data = [np.sin(x * f).tolist() for f in [0.5, 1.0, 1.5, 2.0]]
    ps.lines(data, x.tolist(), ["0.5 Hz", "1 Hz", "1.5 Hz", "2 Hz"], "Sine Waves")
    time.sleep(0.3)
    ps.flush_queue()
    print("   -> 4 sine waves at different frequencies")


def demo_scatter() -> None:
    """Multi-series scatter plot."""
    section("2. Scatter Plot — clusters")
    ps = PlotServer(persist=1)
    clusters_x = [np.random.normal(cx, 0.5, 100).tolist() for cx in [1, 4, 7]]
    clusters_y = [np.random.normal(cy, 0.5, 100).tolist() for cy in [1, 5, 2]]
    ps.scatter(clusters_x, clusters_y, ["A", "B", "C"], "Three Clusters", jitter=False)
    time.sleep(0.3)
    ps.flush_queue()
    print("   -> 3 Gaussian clusters")


def demo_histogram() -> None:
    """Overlapping histograms."""
    section("3. Histogram — distributions")
    ps = PlotServer(persist=1)
    d1 = np.random.normal(0, 1, 2000).tolist()
    d2 = np.random.normal(2, 0.8, 2000).tolist()
    d3 = np.random.normal(-2, 1.5, 2000).tolist()
    ps.histogram([d1, d2, d3], ["N(0,1)", "N(2,0.8)", "N(-2,1.5)"], "Three Distributions")
    time.sleep(0.3)
    ps.flush_queue()
    print("   -> 3 overlapping distributions")


def demo_error_bars() -> None:
    """Error bars showing measurement uncertainty."""
    section("4. Error Bars — measurement uncertainty")
    ps = PlotServer(persist=1)
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
    time.sleep(0.3)
    ps.flush_queue()
    print("   -> Noisy sine with varying error bars")


def demo_filled_curves() -> None:
    """Filled confidence band."""
    section("5. Filled Curves — confidence band")
    ps = PlotServer(persist=1)
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
    time.sleep(0.3)
    ps.flush_queue()
    print("   -> Damped oscillation with expanding confidence band")


def demo_boxplot() -> None:
    """Box-and-whisker plots comparing distributions."""
    section("6. Boxplot — distribution comparison")
    ps = PlotServer(persist=1)
    data = [
        np.random.normal(50, 5, 200).tolist(),
        np.random.normal(60, 10, 200).tolist(),
        np.random.normal(45, 8, 200).tolist(),
        np.random.normal(70, 3, 200).tolist(),
        np.random.normal(55, 15, 200).tolist(),
    ]
    ps.boxplot(data, labels=["Run A", "Run B", "Run C", "Run D", "Run E"], title="Benchmark Scores")
    time.sleep(0.3)
    ps.flush_queue()
    print("   -> 5 benchmark runs with different spread")


def demo_heatmap() -> None:
    """2D heatmap of a Gaussian bump."""
    section("7. Heatmap — 2D field")
    ps = PlotServer(persist=1)
    x = np.linspace(-4, 4, 80)
    y = np.linspace(-4, 4, 80)
    xx, yy = np.meshgrid(x, y, indexing="ij")
    matrix = np.exp(-((xx - 1) ** 2 + yy**2) / 2) + 0.5 * np.exp(
        -((xx + 2) ** 2 + (yy - 1) ** 2) / 1.0
    )
    ps.heatmap(matrix.tolist(), title="Two Gaussian Bumps", colormap="hot")
    time.sleep(0.3)
    ps.flush_queue()
    print("   -> Two overlapping 2D Gaussians")


def demo_steps() -> None:
    """Step plot (staircase) using the style parameter."""
    section("8. Step Plot — discrete signal (via style='fsteps')")
    ps = PlotServer(persist=1)
    data = np.cumsum(np.random.choice([-1, 1], size=50)).astype(float).tolist()
    ps.lines([data], None, ["random walk"], "Discrete Random Walk", "fsteps")
    time.sleep(0.3)
    ps.flush_queue()
    print("   -> Staircase plot of a random walk")


def demo_multiplot_lines() -> None:
    """Multiplot layout with multiple subplots."""
    section("9. Multiplot — panel layout")
    ps = PlotServer(persist=1)
    data = [
        np.sin(np.linspace(0, f * 4 * np.pi, 100) + p).tolist()
        for f, p in zip([1, 2, 3, 4, 0.5, 1.5], [0, 1, 2, 3, 4, 5], strict=True)
    ]
    ps.lines(data, None, [f"ch{i}" for i in range(6)], "6-Channel Signal", "lines", 1)
    time.sleep(0.3)
    ps.flush_queue()
    print("   -> 6-channel signals in a grid layout")


def demo_realtime_stream() -> None:
    """Simulate real-time streaming data."""
    section("10. Real-Time Stream — live updates")
    ps = PlotServer(persist=1)
    window = 100
    data = np.zeros(window)
    print("   Streaming 50 updates... (watch the gnuplot window)")
    for i in range(50):
        data = np.roll(data, -1)
        data[-1] = np.sin(i * 0.2) + np.random.normal(0, 0.1)
        ps.lines([data.tolist()], None, ["live"], f"Frame {i}", "lines")
        time.sleep(0.1)
    ps.flush_queue()
    print("   -> Done streaming")


def main() -> None:
    print("liveplots Demo — demonstrating all plot types\n")
    print("Each plot opens in its own gnuplot window.")
    print("Press Ctrl+C to skip a section.\n")

    demos = [
        demo_lines,
        demo_scatter,
        demo_histogram,
        demo_error_bars,
        demo_filled_curves,
        demo_boxplot,
        demo_heatmap,
        demo_steps,
        demo_multiplot_lines,
        demo_realtime_stream,
    ]

    for demo in demos:
        try:
            demo()
            time.sleep(2)
        except KeyboardInterrupt:
            print("   (skipped)")
            continue

    print(f"\n{'=' * 60}")
    print("  Demo complete! Close the gnuplot windows to exit.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
