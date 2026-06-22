"""ZeroMQ-based plot server and client.

Uses a PUSH/PULL socket pair for fire-and-forget data commands
(scatter, lines, histogram) and a REQ/REP pair for synchronous
control commands (flush_queue, clear_fig, close_plot, set_hold).
"""

from __future__ import annotations

import logging
from queue import Queue
from threading import Thread
from typing import Any

import zmq

from liveplots.plotter import RTplot

logger = logging.getLogger(__name__)

_allocated_ports: set[int] = set()
_servers: list[ZMQPlotServer] = []

_POLL_TIMEOUT_MS = 100
_DEFAULT_CONTROL_TIMEOUT_MS = 30_000
_FLUSH_TIMEOUT_MS = 600_000
_BASE_PORT = 10001

_DATA_METHODS = frozenset(
    {
        "scatter",
        "lines",
        "histogram",
        "error_bars",
        "filled_curves",
        "boxplot",
        "heatmap",
    }
)
_CONTROL_METHODS = frozenset({"clear_fig", "close_plot", "flush_queue", "set_hold"})


class ZMQPlotServer:
    """ZeroMQ plot server with dual sockets.

    Binds a PULL socket for data commands (fire-and-forget from clients)
    and a REP socket for control commands (synchronous request-response).
    Commands are processed by a worker thread via an internal queue.

    Args:
        data_port: TCP port for the PULL (data) socket.
        control_port: TCP port for the REP (control) socket.
        persist: Whether gnuplot windows should persist.
        hold: Whether to hold the previous plot when plotting new data.
    """

    def __init__(
        self,
        data_port: int,
        control_port: int,
        *,
        persist: int = 0,
        hold: bool = False,
    ) -> None:
        self._ctx = zmq.Context.instance()
        self._plotter = RTplot(persist=persist, hold=hold)
        self._queue: Queue[dict[str, Any]] = Queue()
        self._finished = False

        self._pull_socket: zmq.Socket[bytes] = self._ctx.socket(zmq.PULL)
        try:
            self._pull_socket.bind(f"tcp://localhost:{data_port}")
        except zmq.ZMQError:
            self._pull_socket.close()
            raise
        self._pull_socket.rcvtimeo = _POLL_TIMEOUT_MS

        self._rep_socket: zmq.Socket[bytes] = self._ctx.socket(zmq.REP)
        try:
            self._rep_socket.bind(f"tcp://localhost:{control_port}")
        except zmq.ZMQError:
            self._rep_socket.close()
            self._pull_socket.close()
            raise
        self._rep_socket.rcvtimeo = _POLL_TIMEOUT_MS

        self._consumer_thread = Thread(target=self._consume_pull, daemon=True)
        self._worker_thread = Thread(target=self._process_queue, daemon=True)
        self._control_thread = Thread(target=self._handle_control, daemon=True)
        self._consumer_thread.start()
        self._worker_thread.start()
        self._control_thread.start()

    def _consume_pull(self) -> None:
        """Receive data commands from PULL socket and enqueue them."""
        while not self._finished:
            try:
                msg: dict[str, Any] = self._pull_socket.recv_pyobj()
            except zmq.Again:
                continue
            self._queue.put(msg)

    def _process_queue(self) -> None:
        """Process queued data commands by calling plotter methods."""
        while True:
            msg = self._queue.get()
            method = msg["method"]
            args = msg.get("args", ())
            kwargs = msg.get("kwargs", {})
            try:
                func = getattr(self._plotter, method)
                func(*args, **kwargs)
            except Exception:
                logger.exception("Error processing plot command: %s", method)
            self._queue.task_done()

    def _handle_control(self) -> None:
        """Handle synchronous control requests via REP socket."""
        while not self._finished:
            try:
                msg: dict[str, Any] = self._rep_socket.recv_pyobj()
            except zmq.Again:
                continue

            method = msg["method"]
            args = msg.get("args", ())
            kwargs = msg.get("kwargs", {})

            try:
                if method in ("flush_queue", "close_plot"):
                    self._queue.join()
                    result: Any = 0
                else:
                    func = getattr(self._plotter, method)
                    result = func(*args, **kwargs)
                self._rep_socket.send_pyobj({"result": result})
            except Exception:
                logger.exception("Error handling control command: %s", method)
                self._rep_socket.send_pyobj({"error": "internal server error"})

    def stop(self) -> None:
        """Stop the server and close sockets."""
        self._finished = True
        self._pull_socket.close(linger=0)
        self._rep_socket.close(linger=0)


def rpc_plot(port: int = 0, persist: int = 0, hold: bool = False) -> int:
    """Start a ZMQ plot server and return the data port.

    The control port is ``data_port + 1``.

    Args:
        port: Data port to listen on. If 0, the first available port
            pair starting from 10001 is chosen.
        persist: Whether gnuplot windows should persist.
        hold: Whether to hold the previous plot when plotting new data.

    Returns:
        The data port number the server is listening on.
    """
    if port == 0:
        port = _BASE_PORT

    while True:
        if port in _allocated_ports or (port + 1) in _allocated_ports:
            port += 1
            continue
        try:
            server = ZMQPlotServer(port, port + 1, persist=persist, hold=hold)
        except zmq.ZMQError:
            port += 1
            continue

        _allocated_ports.add(port)
        _allocated_ports.add(port + 1)
        _servers.append(server)
        logger.info("Plot server started: data=%s control=%s", port, port + 1)
        return port


class PlotServer:
    """Convenience client that starts a server and connects to it.

    Plot commands (scatter, lines, histogram) are sent via a PUSH socket
    — fire-and-forget with no blocking.

    Control commands (clear_fig, flush_queue, close_plot, set_hold) are
    sent via a REQ socket — synchronous, waits for the server response.

    Args:
        port: Data port to listen on (0 = auto-select).
        persist: Whether gnuplot windows should persist.
    """

    def __init__(self, port: int = 0, persist: int = 1) -> None:
        data_port = rpc_plot(port=port, persist=persist)
        control_port = data_port + 1

        self._ctx = zmq.Context.instance()
        self._push_socket: zmq.Socket[bytes] = self._ctx.socket(zmq.PUSH)
        self._push_socket.connect(f"tcp://localhost:{data_port}")

        self._req_socket: zmq.Socket[bytes] = self._ctx.socket(zmq.REQ)
        self._req_socket.connect(f"tcp://localhost:{control_port}")

    def scatter(self, *args: Any, **kwargs: Any) -> None:
        """Send scatter plot command (fire-and-forget).

        See :meth:`liveplots.plotter.RTplot.scatter` for parameter details.
        """
        self._send_data("scatter", args, kwargs)

    def lines(self, *args: Any, **kwargs: Any) -> None:
        """Send line plot command (fire-and-forget).

        See :meth:`liveplots.plotter.RTplot.lines` for parameter details.
        """
        self._send_data("lines", args, kwargs)

    def histogram(self, *args: Any, **kwargs: Any) -> None:
        """Send histogram command (fire-and-forget).

        See :meth:`liveplots.plotter.RTplot.histogram` for parameter details.
        """
        self._send_data("histogram", args, kwargs)

    def error_bars(self, *args: Any, **kwargs: Any) -> None:
        """Send error bar plot command (fire-and-forget).

        See :meth:`liveplots.plotter.RTplot.error_bars` for parameter details.
        """
        self._send_data("error_bars", args, kwargs)

    def filled_curves(self, *args: Any, **kwargs: Any) -> None:
        """Send filled curves command (fire-and-forget).

        See :meth:`liveplots.plotter.RTplot.filled_curves` for parameter details.
        """
        self._send_data("filled_curves", args, kwargs)

    def boxplot(self, *args: Any, **kwargs: Any) -> None:
        """Send box-and-whisker plot command (fire-and-forget).

        See :meth:`liveplots.plotter.RTplot.boxplot` for parameter details.
        """
        self._send_data("boxplot", args, kwargs)

    def heatmap(self, *args: Any, **kwargs: Any) -> None:
        """Send heatmap command (fire-and-forget).

        See :meth:`liveplots.plotter.RTplot.heatmap` for parameter details.
        """
        self._send_data("heatmap", args, kwargs)

    def clear_fig(self) -> int:
        """Clear the figure (synchronous)."""
        return self._send_control("clear_fig")

    def flush_queue(self) -> int:
        """Block until all queued plot commands have been processed."""
        return self._send_control("flush_queue", timeout=_FLUSH_TIMEOUT_MS)

    def close_plot(self) -> int:
        """Flush the queue and close the plot."""
        return self._send_control("close_plot")

    def set_hold(self, on: bool) -> int:
        """Set hold state of the plot."""
        return self._send_control("set_hold", on)

    def close(self) -> None:
        """Close client sockets."""
        self._push_socket.close(linger=0)
        self._req_socket.close(linger=0)

    def _send_data(self, method: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
        """Send a fire-and-forget command via PUSH socket."""
        self._push_socket.send_pyobj({"method": method, "args": args, "kwargs": kwargs})

    def _send_control(
        self, method: str, *args: Any, timeout: int = _DEFAULT_CONTROL_TIMEOUT_MS
    ) -> int:
        """Send a synchronous command via REQ socket and return the result."""
        self._req_socket.send_pyobj({"method": method, "args": args, "kwargs": {}})
        poller = zmq.Poller()
        poller.register(self._req_socket, zmq.POLLIN)
        events = dict(poller.poll(timeout=timeout))
        if self._req_socket not in events:
            raise TimeoutError(f"Control command '{method}' timed out after {timeout} ms")
        response: dict[str, Any] = self._req_socket.recv_pyobj()
        if "error" in response:
            raise RuntimeError(str(response["error"]))
        return int(response["result"])
