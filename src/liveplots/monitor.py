"""Cross-platform file system monitor based on watchdog."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)

EVENT_MAP: dict[str, str] = {
    "create": "created",
    "delete": "deleted",
    "close_write": "closed",
    "close_nowrite": "closed",
    "access": "modified",
    "attrib": "modified",
    "modify": "modified",
}


class _EventHandler(FileSystemEventHandler):
    """Dispatches file system events to a user callback."""

    def __init__(
        self,
        action: Callable[[str], None],
        event_types: set[str],
        *,
        debug: bool = False,
    ) -> None:
        self.action = action
        self.event_types = event_types
        self.debug = debug

    def _maybe_dispatch(self, event_type: str, src_path: str) -> None:
        if event_type in self.event_types:
            if self.debug:
                logger.debug("%s: %s", event_type, src_path)
            self.action(src_path)

    def on_created(self, event: object) -> None:
        if not _is_dir(event):
            self._maybe_dispatch("created", _get_path(event))

    def on_deleted(self, event: object) -> None:
        if not _is_dir(event):
            self._maybe_dispatch("deleted", _get_path(event))

    def on_modified(self, event: object) -> None:
        if not _is_dir(event):
            self._maybe_dispatch("modified", _get_path(event))

    def on_closed(self, event: object) -> None:
        if not _is_dir(event):
            self._maybe_dispatch("closed", _get_path(event))


def _is_dir(event: object) -> bool:
    return getattr(event, "is_directory", False)


def _get_path(event: object) -> str:
    return getattr(event, "src_path", str(event))


class Monitor:
    """Monitor a file or directory for changes.

    Uses `watchdog <https://python-watchdog.readthedocs.io/>`_ for
    cross-platform file system monitoring.

    Args:
        filepath: Full path of the file or directory to monitor.
        events: List of event names to watch for. Valid events:
            ``create``, ``delete``, ``close_write``, ``close_nowrite``,
            ``access``, ``attrib``, ``modify``.
        action: Callback invoked with the file path when an event fires.
        recursive: Whether to monitor subdirectories recursively.
        debug: Enable debug logging of events.
    """

    def __init__(
        self,
        filepath: str,
        events: list[str],
        action: Callable[[str], None],
        *,
        recursive: bool = True,
        debug: bool = False,
    ) -> None:
        self.filepath = filepath
        self.events = events
        self.action = action

        mapped = self._map_events(events)

        self._observer = Observer()
        handler = _EventHandler(action, mapped, debug=debug)
        self._observer.schedule(handler, filepath, recursive=recursive)
        self._observer.start()
        logger.debug("Monitoring %s for events: %s", filepath, mapped)

    def _map_events(self, events: list[str]) -> set[str]:
        """Map user-facing event names to watchdog event types."""
        mapped: set[str] = set()
        for e in events:
            if e not in EVENT_MAP:
                raise ValueError(f"'{e}' is not a valid event. Valid events: {list(EVENT_MAP)}")
            mapped.add(EVENT_MAP[e])
        return mapped

    def stop(self) -> None:
        """Stop monitoring."""
        self._observer.stop()
        self._observer.join()
