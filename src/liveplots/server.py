"""XML-RPC server for real-time plotting."""

from __future__ import annotations

import logging
import signal
from threading import Thread
from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer

from liveplots.plotter import RTplot

logger = logging.getLogger(__name__)

_ports_in_use: set[int] = set()


class AltXMLRPCServer(SimpleXMLRPCServer):
    """XML-RPC server that can be cleanly shut down via signals.

    Based on https://code.activestate.com/recipes/114579-remotely-exit-a-xmlrpc-server-cleanly/
    """

    finished: bool = False

    def register_signal(self, signum: int) -> None:
        """Register a signal handler that triggers shutdown."""
        signal.signal(signum, self._signal_handler)

    def _signal_handler(self, signum: int, frame: object) -> None:
        logger.info("Caught signal %s, shutting down", signum)
        self.shutdown()

    def shutdown(self) -> int:  # type: ignore[override]
        """Mark the server for shutdown.

        Returns 1 so it can be used as an XML-RPC remote callable.
        """
        self.finished = True
        return 1

    def serve_forever(self, poll_interval: float = 0.5) -> None:
        """Serve requests until :meth:`shutdown` is called."""
        while not self.finished:
            self.handle_request()


def _start_server(server: AltXMLRPCServer, persist: int, hold: bool) -> None:
    """Register a plot instance and serve requests."""
    server.register_instance(RTplot(persist=persist, hold=hold))
    server.register_introspection_functions()
    server.serve_forever()


def rpc_plot(port: int = 0, persist: int = 0, hold: bool = False) -> int:
    """Start an XML-RPC plot server and return the port.

    Args:
        port: Port to listen on. If 0, the first available port
            starting from 10001 is chosen.
        persist: Whether gnuplot windows should persist after the process exits.
        hold: Whether to hold the previous plot when plotting new data.

    Returns:
        The port number the server is listening on.
    """
    if port == 0:
        port = 10001

    while True:
        if port in _ports_in_use:
            port += 1
            continue
        try:
            server = AltXMLRPCServer(("localhost", port), logRequests=False, allow_none=True)
        except OSError:
            port += 1
            continue

        server.register_introspection_functions()
        server.register_function(server.shutdown)

        if hasattr(signal, "SIGHUP"):
            server.register_signal(signal.SIGHUP)
        server.register_signal(signal.SIGINT)

        thread = Thread(target=_start_server, args=(server, persist, hold), daemon=True)
        thread.start()
        break

    _ports_in_use.add(port)
    logger.info("Plot server started on port %s", port)
    return port


class PlotServer(ServerProxy):
    """Convenience client that starts a server and connects to it.

    Args:
        port: Port to listen on (0 = auto-select).
        persist: Whether gnuplot windows should persist.
    """

    def __init__(self, port: int = 0, persist: int = 1) -> None:
        port = rpc_plot(port=port, persist=persist)
        super().__init__(f"http://localhost:{port}", allow_none=True)
