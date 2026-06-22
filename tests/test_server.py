"""Tests for the ZeroMQ server and client."""

from __future__ import annotations

import shutil

import pytest

from liveplots.server import PlotServer, ZMQPlotServer, rpc_plot

requires_gnuplot = pytest.mark.skipif(
    shutil.which("gnuplot") is None, reason="gnuplot not installed"
)


def test_rpc_plot_returns_int() -> None:
    """rpc_plot should return a valid data port number."""
    port = rpc_plot(persist=0)
    assert isinstance(port, int)
    assert port > 0


def test_rpc_plot_increments_port() -> None:
    """When ports are in use, rpc_plot should find the next available pair."""
    port1 = rpc_plot(persist=0)
    port2 = rpc_plot(persist=0)
    assert port1 != port2
    assert abs(port2 - port1) >= 2  # noqa: PLR2004  # each server uses port and port+1


def test_zmq_plot_server_is_class() -> None:
    """ZMQPlotServer should be a class."""
    assert isinstance(ZMQPlotServer, type)


@requires_gnuplot
def test_plot_server_creation() -> None:
    """PlotServer should create a server and connect to it."""
    ps = PlotServer(port=0, persist=0)
    assert ps is not None
    ps.close()


@requires_gnuplot
def test_plot_server_control_roundtrip() -> None:
    """Control commands should return results via REQ/REP."""
    ps = PlotServer(port=0, persist=0)
    assert ps.set_hold(True) == 0
    assert ps.clear_fig() == 0
    assert ps.flush_queue() == 0
    ps.close()
