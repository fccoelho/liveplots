"""Tests for the RTplot plotting class."""

from __future__ import annotations

import shutil
import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from liveplots import PlotServer
from liveplots.plotter import RTplot

requires_gnuplot = pytest.mark.skipif(
    shutil.which("gnuplot") is None, reason="gnuplot not installed"
)


class TestRTplotUnit:
    """Unit tests that mock the gnuplot subprocess (no display needed)."""

    @patch("liveplots.plotter.Popen")
    def test_init(self, mock_popen: MagicMock) -> None:
        mock_popen.return_value.stdin = MagicMock()
        plot = RTplot()
        assert plot.hold is False
        assert plot.plots == []

    @patch("liveplots.plotter.Popen")
    def test_set_hold(self, mock_popen: MagicMock) -> None:
        mock_popen.return_value.stdin = MagicMock()
        plot = RTplot()
        assert plot.set_hold(True) == 0
        assert plot.hold is True

    @patch("liveplots.plotter.Popen")
    def test_clear_fig(self, mock_popen: MagicMock) -> None:
        mock_popen.return_value.stdin = MagicMock()
        plot = RTplot()
        plot.plots = [np.array([1, 2, 3])]
        assert plot.clear_fig() == 0
        assert plot.plots == []


@requires_gnuplot
class TestRTplotIntegration:
    """Integration tests that require a real gnuplot process via ZMQ."""

    def test_lines(self) -> None:
        client = PlotServer(port=0, persist=0)
        data = [np.random.normal(0, 1, 100).tolist() for _ in range(4)]
        client.lines(data, [], ["a", "b", "c", "d"], "Test Lines", "lines", 0)
        time.sleep(0.2)
        client.flush_queue()
        client.close()

    def test_scatter(self) -> None:
        client = PlotServer(port=0, persist=0)
        data1 = np.random.normal(0, 1, 100).tolist()
        data2 = np.random.normal(0, 2, 100).tolist()
        client.scatter(data1, data2, ["d1", "d2"], "test scatter")
        time.sleep(0.2)
        client.flush_queue()
        client.close()

    def test_histogram(self) -> None:
        client = PlotServer(port=0, persist=0)
        data = np.random.normal(0, 1, 1000).tolist()
        client.histogram(data, ["test"], "test histogram")
        time.sleep(0.2)
        client.flush_queue()
        client.close()

    def test_multiple_histogram(self) -> None:
        client = PlotServer(port=0, persist=0)
        data1 = np.random.normal(0, 1, 1000).tolist()
        data2 = np.random.normal(3, 1, 1000).tolist()
        client.histogram([data1, data2], ["test", "test2"], "Multiple histograms")
        time.sleep(0.2)
        client.flush_queue()
        client.close()

    def test_lines_multiplot(self) -> None:
        client = PlotServer(port=0, persist=0)
        data = [np.random.normal(0, 1, 100).tolist() for _ in range(4)]
        client.lines(data, [], ["a", "b", "c", "d"], "Multiplot Lines", "lines", 1)
        time.sleep(0.2)
        client.flush_queue()
        client.close()

    def test_clear_fig(self) -> None:
        client = PlotServer(port=0, persist=0)
        assert client.clear_fig() == 0
        client.close()

    def test_close_plot(self) -> None:
        client = PlotServer(port=0, persist=0)
        data = np.random.normal(0, 1, 100).tolist()
        client.lines([data], [], ["d"], "test")
        time.sleep(0.2)
        assert client.close_plot() == 0
        client.close()

    def test_set_hold(self) -> None:
        client = PlotServer(port=0, persist=0)
        assert client.set_hold(True) == 0
        client.close()

    def test_fire_and_forget_returns_quickly(self) -> None:
        """PUSH commands should return near-instantly."""
        client = PlotServer(port=0, persist=0)
        data = [np.random.normal(0, 1, 1000).tolist() for _ in range(10)]
        t0 = time.perf_counter()
        client.lines(data, [], [f"s{i}" for i in range(10)], "Fast", "lines", 0)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5  # noqa: PLR2004
        client.flush_queue()
        client.close()

    def test_error_bars(self) -> None:
        client = PlotServer(port=0, persist=0)
        x = np.linspace(0, 10, 50)
        y = np.sin(x)
        err = np.abs(np.random.normal(0.1, 0.05, 50))
        client.error_bars(x.tolist(), y.tolist(), err.tolist(), title="Error Bars")
        time.sleep(0.2)
        client.flush_queue()
        client.close()

    def test_filled_curves(self) -> None:
        client = PlotServer(port=0, persist=0)
        x = np.linspace(0, 10, 100)
        mean = np.sin(x)
        std = 0.2 + 0.1 * np.abs(np.cos(x))
        client.filled_curves(
            x.tolist(),
            (mean - std).tolist(),
            (mean + std).tolist(),
            title="Confidence Band",
            fill_color="green",
        )
        time.sleep(0.2)
        client.flush_queue()
        client.close()

    def test_boxplot(self) -> None:
        client = PlotServer(port=0, persist=0)
        data = [np.random.normal(i, 1, 100).tolist() for i in range(4)]
        client.boxplot(data, labels=["A", "B", "C", "D"], title="Distributions")
        time.sleep(0.2)
        client.flush_queue()
        client.close()

    def test_heatmap(self) -> None:
        client = PlotServer(port=0, persist=0)
        x = np.linspace(-3, 3, 50)
        y = np.linspace(-3, 3, 50)
        xx, yy = np.meshgrid(x, y, indexing="ij")
        matrix = np.exp(-(xx**2 + yy**2) / 2)
        client.heatmap(matrix.tolist(), title="2D Gaussian", colormap="jet")
        time.sleep(0.2)
        client.flush_queue()
        client.close()
