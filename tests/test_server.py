"""Tests for the XML-RPC server."""

from __future__ import annotations

import shutil
from xmlrpc.server import SimpleXMLRPCServer

import pytest

from liveplots.server import AltXMLRPCServer, PlotServer, rpc_plot

requires_gnuplot = pytest.mark.skipif(
    shutil.which("gnuplot") is None, reason="gnuplot not installed"
)


def test_rpc_plot_returns_int() -> None:
    """rpc_plot should return a valid port number."""
    port = rpc_plot(persist=0)
    assert isinstance(port, int)
    assert port > 0


def test_rpc_plot_increments_port() -> None:
    """When a port is in use, rpc_plot should find the next available one."""
    port1 = rpc_plot(persist=0)
    port2 = rpc_plot(persist=0)
    assert port1 != port2


@requires_gnuplot
def test_plot_server_creation() -> None:
    """PlotServer should create a server and connect to it."""
    ps = PlotServer(port=0, persist=0)
    assert ps is not None
    ps.close_plot()


def test_alt_xmlrpc_server_is_subclass() -> None:
    """AltXMLRPCServer should subclass SimpleXMLRPCServer."""
    assert issubclass(AltXMLRPCServer, SimpleXMLRPCServer)
