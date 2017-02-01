from __future__ import absolute_import
from nose import SkipTest
from nose.tools import assert_equal
from liveplots.filemonitor import Monitor
import os
import pyinotify


class TestMonitor:
    def test___init__(self):
        monitor = Monitor('/tmp', ['create'], lambda x: 1, debug=1)
        assert isinstance(monitor, Monitor)

    def test__get_mask(self):
        monitor = Monitor('/tmp', ['create'], lambda x: 1, debug=1)
        assert monitor.mask == pyinotify.IN_CREATE
        monitor = Monitor('/tmp', ['create', 'delete'], lambda x: 1, debug=1)
        assert monitor.mask == pyinotify.IN_CREATE | pyinotify.IN_DELETE


class test__HandleEvents:
    def test_process_IN_ACCESS(self):
        f = open('/tmp/test', 'w')
        monitor = Monitor('/tmp/test', ['access'], lambda x: 1, debug=1)
        f.write('kjl')
        f.close()

    def test_process_IN_ATTRIB(self):
        # __handle_events = _HandleEvents()
        # assert_equal(expected, __handle_events.process_IN_ATTRIB(event))
        raise SkipTest  # TODO: implement your test here

    def test_process_IN_CLOSE_NOWRITE(self):
        f = open('/tmp/test', 'r')
        monitor = Monitor('/tmp/test', ['close_nowrite'], lambda x: 1, debug=1)
        f.close()

    def test_process_IN_CLOSE_WRITE(self):
        f = open('/tmp/test', 'w')
        monitor = Monitor('/tmp/test', ['close_write'], lambda x: 1, debug=1)
        f.write('kjl')
        f.close()

    def test_process_IN_CREATE(self):
        monitor = Monitor('/tmp', ['create'], lambda x: 1, debug=1)
        f = open('/tmp/test', 'w')
        f.close()

    def test_process_IN_DELETE(self):
        f = open('/tmp/test', 'w')
        f.close()
        monitor = Monitor('/tmp/test', ['delete'], lambda x: 1, debug=1)
        os.unlink('/tmp/test')

    def test_process_IN_MODIFY(self):
        f = open('/tmp/test', 'w')
        monitor = Monitor('/tmp/test', ['modify'], lambda x: 1, debug=1)
        f.write('kjl')
        f.close()

    def test_set_action(self):
        action = lambda x: 1
        monitor = Monitor('/tmp/test', ['modify'], action, debug=1)
        assert monitor.handler.action == action
