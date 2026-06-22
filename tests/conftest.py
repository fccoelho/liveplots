"""Shared pytest fixtures and configuration."""

from __future__ import annotations

import shutil
from collections.abc import Iterator

import pytest

from liveplots.server import PlotServer

has_gnuplot = shutil.which("gnuplot") is not None
requires_gnuplot = pytest.mark.skipif(not has_gnuplot, reason="gnuplot not installed")


@pytest.fixture
def plot_server() -> Iterator[PlotServer]:
    """Start a plot server and yield a PlotServer client."""
    ps = PlotServer(port=0, persist=0)
    yield ps
    ps.flush_queue()
    ps.close()
