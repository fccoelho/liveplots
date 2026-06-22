"""Tests for the RTplot plotting class."""

from __future__ import annotations

import shutil
from unittest.mock import MagicMock, patch
from xmlrpc.client import ServerProxy

import numpy as np
import pytest

from liveplots.plotter import RTplot
from liveplots.server import rpc_plot

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

    @patch("liveplots.plotter.Popen")
    def test_flush_queue(self, mock_popen: MagicMock) -> None:
        mock_popen.return_value.stdin = MagicMock()
        plot = RTplot()
        assert plot.flush_queue() == 0


@requires_gnuplot
class TestRTplotIntegration:
    """Integration tests that require a real gnuplot process."""

    def test_lines(self) -> None:
        port = rpc_plot(persist=0)
        client = ServerProxy(f"http://localhost:{port}", allow_none=True)
        data = [np.random.normal(0, 1, 100).tolist() for _ in range(4)]
        client.lines(data, [], ["a", "b", "c", "d"], "Test Lines", "lines", 0)
        client.close_plot()

    def test_scatter(self) -> None:
        port = rpc_plot(persist=0)
        client = ServerProxy(f"http://localhost:{port}", allow_none=True)
        data1 = np.random.normal(0, 1, 100).tolist()
        data2 = np.random.normal(0, 2, 100).tolist()
        client.scatter(data1, data2, ["d1", "d2"], "test scatter")
        client.close_plot()

    def test_histogram(self) -> None:
        port = rpc_plot(persist=0)
        client = ServerProxy(f"http://localhost:{port}", allow_none=True)
        data = np.random.normal(0, 1, 1000).tolist()
        client.histogram(data, ["test"], "test histogram")
        client.close_plot()

    def test_multiple_histogram(self) -> None:
        port = rpc_plot(persist=0)
        client = ServerProxy(f"http://localhost:{port}", allow_none=True)
        data1 = np.random.normal(0, 1, 1000).tolist()
        data2 = np.random.normal(3, 1, 1000).tolist()
        client.histogram([data1, data2], ["test", "test2"], "Multiple histograms")
        client.close_plot()

    def test_lines_multiplot(self) -> None:
        port = rpc_plot(persist=0)
        client = ServerProxy(f"http://localhost:{port}", allow_none=True)
        data = [np.random.normal(0, 1, 100).tolist() for _ in range(4)]
        client.lines(data, [], ["a", "b", "c", "d"], "Multiplot Lines", "lines", 1)
        client.close_plot()

    def test_clear_fig_via_rpc(self) -> None:
        port = rpc_plot(persist=0)
        client = ServerProxy(f"http://localhost:{port}", allow_none=True)
        assert client.clear_fig() == 0
        client.close_plot()

    def test_close_plot_via_rpc(self) -> None:
        port = rpc_plot(persist=0)
        client = ServerProxy(f"http://localhost:{port}", allow_none=True)
        assert client.close_plot() == 0
