from nose import SkipTest
from nose.tools import assert_equal
from graphserver.xmlrpc import RTplot
from graphserver import xmlrpc
from numpy import random

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
        data = random.normal(0,1,1000).tolist()
        r_tplot = RTplot(persist=0, debug=0)
        r_tplot.histogram(data, ['test'], 'test title')
        
    def test_lines(self):
        data = random.normal(0,1,1000).tolist()
        r_tplot = RTplot(persist=0, debug=0)
        r_tplot.lines(data,None, ['test'], 'test title')
        

    def test_scatter(self):
        data = random.normal(0,1,1000).tolist()
        data2 = random.normal(0,2,1000).tolist()
        r_tplot = RTplot(persist=0, debug=0)
        r_tplot.scatter(data,data2, ['d1','d2'], 'test scatter')
        

class TestStartServer:
    def test_start_server(self):
        #assert_equal(expected, start_server(server))
        raise SkipTest # TODO: implement your test here

class TestRpcPlot:
    def test_rpc_plot(self):
        assert_equal(9800, xmlrpc.rpc_plot(9800))


