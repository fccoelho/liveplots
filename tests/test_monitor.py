"""Tests for the file system monitor."""

from __future__ import annotations

import pathlib
import time

import pytest

from liveplots.monitor import EVENT_MAP, Monitor


def test_monitor_creation(tmp_path: object) -> None:
    """Monitor should be created successfully."""
    events = ["create", "delete"]
    monitor = Monitor(str(tmp_path), events, lambda x: None)
    assert isinstance(monitor, Monitor)
    monitor.stop()


def test_invalid_event_raises(tmp_path: object) -> None:
    """An invalid event name should raise ValueError."""
    with pytest.raises(ValueError, match="not a valid event"):
        Monitor(str(tmp_path), ["invalid_event"], lambda x: None)


def test_event_map_has_all_expected_events() -> None:
    """The event map should cover all documented events."""
    expected = {"create", "delete", "close_write", "close_nowrite", "modify", "move", "open"}
    assert expected == set(EVENT_MAP)


def test_monitor_triggers_action_on_create(tmp_path: object) -> None:
    """The action callback should fire when a file is created."""
    results: list[str] = []
    monitor = Monitor(str(tmp_path), ["create"], results.append, debug=True)

    file_path = pathlib.Path(str(tmp_path)) / "test_file.txt"
    file_path.write_text("hello")

    time.sleep(0.5)
    monitor.stop()

    assert len(results) > 0
    assert str(file_path) in results


def test_monitor_triggers_action_on_modify(tmp_path: object) -> None:
    """The action callback should fire when a file is modified."""
    file_path = pathlib.Path(str(tmp_path)) / "existing.txt"
    file_path.write_text("initial")

    results: list[str] = []
    monitor = Monitor(str(tmp_path), ["modify"], results.append, debug=True)

    time.sleep(0.2)
    file_path.write_text("modified")

    time.sleep(0.5)
    monitor.stop()

    assert len(results) > 0


def test_monitor_stop(tmp_path: object) -> None:
    """Monitor.stop() should stop the observer."""
    monitor = Monitor(str(tmp_path), ["create"], lambda x: None)
    monitor.stop()
