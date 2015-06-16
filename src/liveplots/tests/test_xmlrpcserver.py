from __future__ import absolute_import
from nose import SkipTest
from nose.tools import assert_equal
from liveplots.xmlrpcserver import rpc_plot
from liveplots import xmlrpcserver
import six.moves.xmlrpc_client
from numpy import random


class TestRTplot:
    def setUp(self):
        port = rpc_plot(persist=0)
        self.r_tplot = six.moves.xmlrpc_client.ServerProxy('http://localhost:%s'%port)

    def tearDown(self):
        pass
        self.r_tplot.flush_queue()
        self.r_tplot.shutdown()

    def test___init__(self):
        port = rpc_plot(persist=0)
        assert isinstance(port, int)

    def test_clearFig(self):
        assert_equal(0, self.r_tplot.clearFig())

    def test_close_plot(self):
        assert_equal(0, self.r_tplot.close_plot())

    def test_histogram(self):
        data = random.normal(0, 1, 1000).tolist()
        self.r_tplot.histogram(data, ['test'], 'test histogram')
        self.r_tplot.close_plot()

    def test_lines(self):
        data = random.normal(0, 1, 1000).tolist()
        self.r_tplot.lines(data, [], ['test'], 'test title')
        self.r_tplot.close_plot()

    def test_scatter(self):
        data = random.normal(0, 1, 1000).tolist()
        data2 = random.normal(0, 2, 1000).tolist()
        self.r_tplot.scatter(data, data2, ['d1', 'd2'], 'test scatter')
        self.r_tplot.close_plot()


class TestStartServer:
    def test_start_server(self):
        # assert_equal(expected, start_server(server))
        raise SkipTest  # TODO: implement your test here

        # ~ class TestRpcPlot:
        # ~ def test_rpc_plot(self):
        # ~ assert_equal(9802, xmlrpcserver.rpc_plot(9802))
