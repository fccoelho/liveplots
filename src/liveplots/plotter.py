"""Gnnuplot-based real-time plotting."""

from __future__ import annotations

import functools
import logging
from queue import Queue
from subprocess import PIPE, Popen
from threading import Thread
from typing import TYPE_CHECKING, Any, TypeVar, cast

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

logger = logging.getLogger(__name__)

_NUM_LABELS_1D = 2
_NDIM_2D = 2
_NDIM_3D = 3
_MULTI_LAYOUT_THRESHOLD = 0.5
_HIST_BINS = 50

F = TypeVar("F", bound="Callable[..., Any]")


def _enqueue(func: F) -> F:  # noqa: UP047
    """Decorator that places the call on the instance's work queue.

    Plotting methods decorated with this return immediately; the
    actual gnuplot interaction happens asynchronously in a worker thread.
    Use :meth:`RTplot.flush_queue` to block until all queued work is done.
    """

    @functools.wraps(func)
    def wrapper(self: RTplot, *args: Any, **kwargs: Any) -> Any:
        self._queue.put((func, (self, *args), kwargs))

    return cast("F", wrapper)


class RTplot:
    """Real-time plotting class based on Gnuplot.

    Maintains a FIFO queue of plotting calls consumed sequentially
    by a worker thread, so plot commands don't block the caller.
    """

    def __init__(self, *, persist: int = 0, hold: bool = False) -> None:
        self._gp = self._spawn_gnuplot(persist)
        self.plots: list[np.ndarray] = []
        self._queue: Queue[tuple[Callable[..., Any], tuple[Any, ...], dict[str, Any]]] = Queue()
        self.persist = persist
        self.hold = hold
        self._worker_thread = Thread(target=self._worker, daemon=True)
        self._worker_thread.start()

    def _spawn_gnuplot(self, persist: int) -> Popen[bytes]:
        cmd = ["gnuplot"]
        if persist:
            cmd.append("-persist")
        return Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    def _worker(self) -> None:
        while True:
            func, args, kwargs = self._queue.get()
            try:
                func(*args, **kwargs)
            except Exception:
                logger.exception("Error in plot worker thread")
            self._queue.task_done()

    def set_hold(self, on: bool) -> int:
        """Set hold state of the plot.

        Args:
            on: Whether to hold the previous plot.
        """
        self.hold = on
        return 0

    def clear_fig(self) -> int:
        """Clear the figure."""
        self.plots = []
        return 0

    def close_plot(self) -> int:
        """Flush the queue and close the plot."""
        self._queue.join()
        return 0

    def flush_queue(self) -> int:
        """Block until all queued plot commands have been processed."""
        self._queue.join()
        return 0

    @_enqueue
    def scatter(
        self,
        x: list[float] | list[list[float]],
        y: list[float] | list[list[float]],
        labels: list[str] | None = None,
        title: str = "",
        style: str = "points",
        jitter: bool = True,
        multiplot: int = 0,
    ) -> int:
        """Make scatter plots from data.

        If ``x`` and ``y`` are multidimensional (lists of lists), multiple
        scatter plots will be generated, pairing rows.

        Args:
            x: List of numbers or list of lists.
            y: List of numbers or list of lists.
            labels: List of variable names for the legend.
            title: Title of the plot.
            style: Gnuplot plot style (e.g. ``'points'``).
            jitter: Whether to apply small jitter to avoid overlapping points.
            multiplot: Whether to make multiple subplots.

        Returns:
            0 on success.
        """
        if labels is None:
            labels = []

        if len(x) != len(y):
            raise ValueError("x and y must have the same length")

        x_arr = np.asarray(x, dtype=float)
        y_arr = np.asarray(y, dtype=float)

        if x_arr.shape != y_arr.shape:
            raise ValueError(f"x {x_arr.shape} and y {y_arr.shape} must have the same shape")

        self._validate_scatter_labels(labels, x_arr)

        jt = float(np.random.normal(1, 1e-4, 1)[0]) if jitter else 1.0

        if not labels:
            labels = [f"s{i}" for i in range(x_arr.shape[0])]

        single = bool(multiplot)
        if single:
            self._write_multiplot_layout(len(x_arr), title)
        else:
            self._write(f'set title "{title}"')

        if x_arr.ndim == _NDIM_2D:
            self._scatter_multi(x_arr, y_arr, jt, labels, style, single, bool(multiplot))
        elif x_arr.ndim > _NDIM_2D:
            logger.warning("scatter() does not support arrays with >2 dimensions")
        else:
            self._scatter_single(x_arr, y_arr, jt, labels, style, single, bool(multiplot))

        if not self.hold:
            self.plots = []
        return 0

    def _validate_scatter_labels(self, labels: list[str], x_arr: np.ndarray) -> None:
        """Validate label count against data shape."""
        if not labels:
            return
        if x_arr.ndim == 1:
            if len(labels) != _NUM_LABELS_1D:
                raise ValueError(
                    f"Labels list should contain exactly {_NUM_LABELS_1D} elements, "
                    f"but has {len(labels)}"
                )
        elif len(labels) != x_arr.shape[0]:
            raise ValueError(
                f"labels list must have exactly {x_arr.shape[0]} items, but has {len(labels)}"
            )

    def _scatter_multi(
        self,
        x_arr: np.ndarray,
        y_arr: np.ndarray,
        jt: float,
        labels: list[str],
        style: str,
        single: bool,
        multiplot: bool,
    ) -> None:
        """Plot 2D scatter data (multiple series)."""
        if not single:
            self._write("plot " + ",".join(f"'-' title '{label}' with {style}" for label in labels))
        for n in range(x_arr.shape[0]):
            d = zip(x_arr[n] * jt, y_arr[n] * jt, strict=True)
            self._plot_data(d, label=labels[n], style=style, single=single)
        if multiplot:
            self._write("unset multiplot")

    def _scatter_single(
        self,
        x_arr: np.ndarray,
        y_arr: np.ndarray,
        jt: float,
        labels: list[str],
        style: str,
        single: bool,
        multiplot: bool,
    ) -> None:
        """Plot 1D scatter data (single series)."""
        x_arr = x_arr * jt
        y_arr = y_arr * jt
        d = zip(x_arr, y_arr, strict=True)
        if not single:
            self._write(f"plot '-' title '{labels[0]}' with {style}")
        self._plot_data(d, label=labels[0], style=style, single=single)
        if multiplot:
            self._write("unset multiplot")

    @_enqueue
    def lines(
        self,
        data: list[list[float]],
        x: list[float] | None = None,
        labels: list[str] | None = None,
        title: str = "",
        style: str = "lines",
        multiplot: int = 0,
    ) -> int:
        """Create a single or multiple line plot.

        Args:
            data: Must be a list of lists (one inner list per series).
            x: X-axis values for the series. If omitted, indices are used.
            labels: Legend labels for each series.
            title: Plot title.
            style: Gnuplot style (``'lines'``, ``'boxes'``, ``'points'``, etc.).
            multiplot: Whether to make multiple subplots.

        Returns:
            0 on success.
        """
        if not isinstance(data, list):
            raise TypeError("data must be a list")

        if not isinstance(data[0], list):
            logger.debug("Converting data into list of lists")
            data = [data]

        if len(data[0]) == 0:
            raise ValueError("No data provided")

        try:
            data_arr = np.asarray(data, dtype=float)
        except ValueError:
            logger.error("Failed to convert data to float array: %s", data)
            raise

        x_arr = np.asarray(x, dtype=float) if x else None

        if labels is None:
            labels = [f"S_{i}" for i in range(len(data_arr))]

        if multiplot:
            self._lines_multiplot(data_arr, x_arr, labels, title, style)
        else:
            self._lines_single_plot(data_arr, x_arr, labels, title, style)

        return 0

    def _lines_multiplot(
        self,
        data_arr: np.ndarray,
        x_arr: np.ndarray | None,
        labels: list[str],
        title: str,
        style: str,
    ) -> None:
        """Plot lines in multiplot mode."""
        self._write_multiplot_layout(len(data_arr), title)
        if data_arr.ndim > 1:
            for row, label in zip(data_arr, labels, strict=True):
                x_vals = x_arr if x_arr is not None else np.arange(len(row))
                d = zip(x_vals, row, strict=True)
                self._plot_data(d, label=label, style=style, single=True)
        else:
            x_vals = x_arr if x_arr is not None else np.arange(len(data_arr))
            d = zip(x_vals, data_arr, strict=True)
            self._plot_data(d, style=style, single=True)
        self._write("unset multiplot")

    def _lines_single_plot(
        self,
        data_arr: np.ndarray,
        x_arr: np.ndarray | None,
        labels: list[str],
        title: str,
        style: str,
    ) -> None:
        """Plot lines in single-plot mode."""
        self._write(f'set title "{title}"')
        if data_arr.ndim > 1:
            self._write(
                "plot " + ",".join(f" '-' title '{label}'  with {style}" for label in labels)
            )
            for row, label in zip(data_arr, labels, strict=True):
                x_vals = x_arr if x_arr is not None else np.arange(len(row))
                d = zip(x_vals, row, strict=True)
                self._plot_data(d, label=label, style=style)
        else:
            x_vals = x_arr if x_arr is not None else np.arange(len(data_arr))
            d = zip(x_vals, data_arr, strict=True)
            self._write(f"plot '-' with {style}")
            self._plot_data(d, style=style)

    @_enqueue
    def histogram(
        self,
        data: list[float] | list[list[float]],
        labels: list[str] | None = None,
        title: str = "",
        multiplot: int = 0,
    ) -> int:
        """Create a single or multiple histogram plot.

        Args:
            data: Must be a list (of lists for multiple histograms).
            labels: Legend labels for each series.
            title: Plot title.
            multiplot: Whether to make multiple subplots.

        Returns:
            0 on success.
        """
        if not isinstance(data, list):
            raise TypeError("data must be a list")

        data_arr = np.asarray(data)

        if labels is None:
            labels = [f"Var_{i}" for i in range(data_arr.shape[0])]

        self._write("set style data histograms")
        self._write("set style fill solid border -1")

        single = bool(multiplot)
        if single:
            self._write_multiplot_layout(len(data_arr), title)
        else:
            self._write(f'set title "{title}"')

        if data_arr.ndim == _NDIM_2D:
            self._histogram_multi(data_arr, labels, single, bool(multiplot))
        elif data_arr.ndim > _NDIM_2D:
            logger.warning("histogram() does not support arrays with >2 dimensions")
        else:
            self._histogram_single(data_arr, labels, single, bool(multiplot))

        if not self.hold:
            self.plots = []
        return 0

    def _histogram_multi(
        self,
        data_arr: np.ndarray,
        labels: list[str],
        single: bool,
        multiplot: bool,
    ) -> None:
        """Plot multiple histograms (2D data)."""
        if not single:
            self._write("plot " + ",".join(f" '-' title '{label}' with boxes" for label in labels))
        for n, row in enumerate(data_arr):
            counts, bins = np.histogram(row, density=True, bins=_HIST_BINS)
            d = list(zip(bins[:-1], counts, strict=True))
            self._plot_data(d, label=labels[n], style="boxes", single=single)
        if multiplot:
            self._write("unset multiplot")

    def _histogram_single(
        self,
        data_arr: np.ndarray,
        labels: list[str],
        single: bool,
        multiplot: bool,
    ) -> None:
        """Plot a single histogram (1D data)."""
        counts, bins = np.histogram(data_arr, density=True, bins=_HIST_BINS)
        d = list(zip(bins[:-1], counts, strict=True))
        if not single:
            self._write(f"plot '-' title '{labels[0]}' with boxes")
        self._plot_data(d, label=labels[0], style="boxes", single=single)
        if multiplot:
            self._write("unset multiplot")

    def _write_multiplot_layout(self, n: int, title: str) -> None:
        """Write the multiplot layout command."""
        sq = np.sqrt(n)
        ad = 1 if sq % 1 > _MULTI_LAYOUT_THRESHOLD else 0
        r = int(np.floor(sq))
        c = int(np.ceil(sq)) + ad
        if n == _NDIM_3D:
            r, c = 3, 1
        self._write(f'set multiplot layout {r},{c} title "{title}"')

    def _write(self, cmd: str) -> None:
        """Write a command string to the gnuplot process."""
        assert self._gp.stdin is not None
        self._gp.stdin.write((cmd + "\n").encode())
        self._gp.stdin.flush()

    def _plot_data(
        self,
        data: Iterable[tuple[float, ...]],
        *,
        label: str = "data",
        style: str = "lines",
        single: bool = False,
    ) -> None:
        """Write inline data to the gnuplot process."""
        rows = list(data)
        lines = [" ".join(str(v) for v in row) for row in rows]
        payload = ("\n".join(lines) + "\ne\n").encode()

        if single:
            self._write(f"plot '-' title '{label}' with {style}")

        try:
            assert self._gp.stdin is not None
            self._gp.stdin.write(payload)
        except BrokenPipeError:
            logger.warning("Gnuplot process died, respawning...")
            self._gp = self._spawn_gnuplot(self.persist)
            assert self._gp.stdin is not None
            self._gp.stdin.write(payload)
        self._gp.stdin.flush()
