from nose import SkipTest
from nose.tools import assert_equal
from graphserver.xmlrpc import RTplot
from graphserver import xmlrpc

class TestRTplot:
    def test___init__(self):
        r_tplot = RTplot(persist=0, debug=0)
        assert isinstance(r_tplot, RTplot)
        

    def test_clearFig(self):
        # r_tplot = RTplot(persist, debug)
        # assert_equal(expected, r_tplot.clearFig())
        raise SkipTest # TODO: implement your test here

    def test_close_plot(self):
        # r_tplot = RTplot(persist, debug)
        # assert_equal(expected, r_tplot.close_plot())
        raise SkipTest # TODO: implement your test here

    def test_histogram(self):
        # r_tplot = RTplot(persist, debug)
        # assert_equal(expected, r_tplot.histogram(data, title, names))
        raise SkipTest # TODO: implement your test here

    def test_lines(self):
        # r_tplot = RTplot(persist, debug)
        # assert_equal(expected, r_tplot.lines(data, x, names, title, style))
        raise SkipTest # TODO: implement your test here

    def test_scatter(self):
        # r_tplot = RTplot(persist, debug)
        # assert_equal(expected, r_tplot.scatter(x, y, names, title, style, jitter))
        raise SkipTest # TODO: implement your test here

class TestStartServer:
    def test_start_server(self):
        #assert_equal(expected, start_server(server))
        raise SkipTest # TODO: implement your test here

class TestRpcPlot:
    def test_rpc_plot(self):
        assert_equal(9800, xmlrpc.rpc_plot(9800))


