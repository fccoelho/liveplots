"""Shared pytest fixtures and configuration."""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from xmlrpc.client import ServerProxy

import pytest

from liveplots.server import rpc_plot

has_gnuplot = shutil.which("gnuplot") is not None
requires_gnuplot = pytest.mark.skipif(not has_gnuplot, reason="gnuplot not installed")


@pytest.fixture
def plot_server() -> Iterator[object]:
    """Start a plot server and yield a ServerProxy-like client."""
    port = rpc_plot(persist=0)
    client = ServerProxy(f"http://localhost:{port}", allow_none=True)
    yield client
    client.close_plot()
