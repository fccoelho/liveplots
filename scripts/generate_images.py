"""Generate PNG screenshots of each plot type for the README."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from liveplots.plotter import RTplot

OUT = Path(__file__).resolve().parent.parent / "docs" / "images"
OUT.mkdir(parents=True, exist_ok=True)

SIZE = "set terminal pngcairo size 800,500 enhanced font 'Arial,12'"
np.random.seed(42)


def save(plotter: RTplot, name: str) -> None:
    plotter._write(f"set output '{OUT / name}'")
    plotter._gp.stdin.flush()
    print(f"  saved {name}")


def make_plotter() -> RTplot:
    p = RTplot(persist=0)
    p._write(SIZE)
    return p


def gen_lines() -> None:
    p = make_plotter()
    save(p, "lines.png")
    x = np.linspace(0, 4 * np.pi, 200)
    data = [np.sin(x * f).tolist() for f in [0.5, 1.0, 1.5, 2.0]]
    p.lines(data, x.tolist(), ["0.5 Hz", "1 Hz", "1.5 Hz", "2 Hz"], "Sine Waves")


def gen_scatter() -> None:
    p = make_plotter()
    save(p, "scatter.png")
    x = [np.random.normal(cx, 0.5, 100).tolist() for cx in [1, 4, 7]]
    y = [np.random.normal(cy, 0.5, 100).tolist() for cy in [1, 5, 2]]
    p.scatter(x, y, ["A", "B", "C"], "Three Clusters", jitter=False)


def gen_histogram() -> None:
    p = make_plotter()
    save(p, "histogram.png")
    d1 = np.random.normal(0, 1, 2000).tolist()
    d2 = np.random.normal(2, 0.8, 2000).tolist()
    d3 = np.random.normal(-2, 1.5, 2000).tolist()
    p.histogram([d1, d2, d3], ["N(0,1)", "N(2,0.8)", "N(-2,1.5)"], "Three Distributions")


def gen_error_bars() -> None:
    p = make_plotter()
    save(p, "error_bars.png")
    x = np.linspace(0, 10, 30)
    y = 2 * np.sin(x) + np.random.normal(0, 0.3, 30)
    err = 0.3 + 0.2 * np.random.rand(30)
    p.error_bars(
        x.tolist(),
        y.tolist(),
        err.tolist(),
        labels=["sensor"],
        title="Sensor Readings",
    )


def gen_filled_curves() -> None:
    p = make_plotter()
    save(p, "filled_curves.png")
    x = np.linspace(0, 10, 200)
    mean = np.sin(x) * np.exp(-0.2 * x)
    lower = mean - 0.3 - 0.1 * x
    upper = mean + 0.3 + 0.1 * x
    p.filled_curves(
        x.tolist(),
        lower.tolist(),
        upper.tolist(),
        labels=["band"],
        title="Damped Sine ± Confidence",
        fill_color="purple",
    )


def gen_boxplot() -> None:
    p = make_plotter()
    save(p, "boxplot.png")
    data = [
        np.random.normal(50, 5, 200).tolist(),
        np.random.normal(60, 10, 200).tolist(),
        np.random.normal(45, 8, 200).tolist(),
        np.random.normal(70, 3, 200).tolist(),
        np.random.normal(55, 15, 200).tolist(),
    ]
    p.boxplot(data, labels=["A", "B", "C", "D", "E"], title="Benchmark Scores")


def gen_heatmap() -> None:
    p = make_plotter()
    save(p, "heatmap.png")
    x = np.linspace(-4, 4, 80)
    y = np.linspace(-4, 4, 80)
    xx, yy = np.meshgrid(x, y, indexing="ij")
    matrix = np.exp(-((xx - 1) ** 2 + yy**2) / 2) + 0.5 * np.exp(
        -((xx + 2) ** 2 + (yy - 1) ** 2) / 1.0
    )
    p.heatmap(matrix.tolist(), title="Two Gaussian Bumps", colormap="hot")


def gen_multiplot() -> None:
    p = make_plotter()
    save(p, "multiplot.png")
    data = [
        np.sin(np.linspace(0, f * 4 * np.pi, 100) + ph).tolist()
        for f, ph in zip([1, 2, 3, 4, 0.5, 1.5], [0, 1, 2, 3, 4, 5], strict=True)
    ]
    p.lines(data, None, [f"ch{i}" for i in range(6)], "6-Channel Signal", "lines", 1)


GENS = [
    ("lines", gen_lines),
    ("scatter", gen_scatter),
    ("histogram", gen_histogram),
    ("error_bars", gen_error_bars),
    ("filled_curves", gen_filled_curves),
    ("boxplot", gen_boxplot),
    ("heatmap", gen_heatmap),
    ("multiplot", gen_multiplot),
]


def main() -> None:
    for name, fn in GENS:
        print(f"Generating {name}...")
        fn()
    print(f"\nAll plots saved to {OUT}/")


if __name__ == "__main__":
    sys.exit(main())
