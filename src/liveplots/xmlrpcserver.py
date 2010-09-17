__author__="fccoelho@gmail.com"
__date__ ="$26/02/2009 10:44:29$"
__docformat__ = "restructuredtext en"

import Gnuplot
import numpy
from SimpleXMLRPCServer import SimpleXMLRPCServer
#from twisted.web import xmlrpc, server
#from twisted.internet import reactor
from multiprocessing import Process
from threading import Thread, Lock
from Queue import Queue
import time
import signal

Gnuplot.GnuplotOpts.prefer_inline_data = 1
Gnuplot.GnuplotOpts.prefer_fifo_data = 0

__ports_used = []

Q = Queue()
def worker():
    while True:
        item = Q.get()
        item[0](*item[1])
        Q.task_done()
        

def enqueue(f):
    """Decorator that places the call on a queue"""
    def queued(self,*args,**kw):
        Q.put((f,(self,)+args))
    queued.__doc__ = f.__doc__
    queued.__name__ = f.__name__
    return queued
    
class RTplot():
    '''
    Real time plotting class based on Gnuplot
    '''
    def __init__(self, persist=0,debug=0,**kwargs):
        self.gp = Gnuplot.Gnuplot(persist = persist, debug=debug)
        self.plots = []
        self.Queue = Q
        self.persist = persist
        self.hold = 0 if 'hold' not in kwargs else kwargs['hold']
        t= Thread(target=worker,args=())
        t.setDaemon(True)
        t.start()
    
    def set_hold(self,on):
        '''
        Sets hold state of the plot.
        takes 0 or 1 as argument
        '''
        self.hold = on
    
    def clearFig(self):
        '''
        Clears the figure.
        '''
        self.plots = []
        return 0 
        #self.gp.reset()
    def close_plot(self):
        self.flush_queue()
        if self.persist:
            self.gp.close()
        return 0 

    def flush_queue(self):
        self.Queue.join()
        return 0
    
    @enqueue
    def scatter(self,x,y,labels=[],title='',style='points', jitter=True, multiplot=0):
        """
        Makes scatter plots from numpy arrays.
        if x and are multidimensional(lists of lists), multiple scatter plots will be generated, pairing rows.
        
        :Parameters:
            -`x`: list of numbers or list of lists
            -`y`: list of numbers or list of lists
            -`labels`: list of strings (variable names)
            -`title`: Title of the plot
        """
        assert len(x)==len(y)
        if multiplot:
            sq = numpy.sqrt(len(x))
            ad = 1 if sq%1 >0.5 else 0
            r= numpy.floor(sq);c=numpy.ceil(sq)+ad
            if len(x) == 3:
                r=3;c=1
            self.gp('set multiplot layout %s,%s title "%s"'%(r, c, title))
        else:
            self.gp('set title "%s"'%title)
        if jitter:
            jt = numpy.random.normal(1, 1e-4,1)[0]
        else:
            jt = 1
        x = numpy.array(x)
        y = numpy.array(y)
        
        if x.shape != y.shape:
            raise ValueError("x, %s and y, %s arrays must have the same shape."%(x.shape,y.shape))
        if labels:
            if len(x.shape)==1:
                if len(labels) !=2:
                    raise ValueError("Labels list should contain exactly 2 elements, but has %s"%len(labels))
            else:
                if len(labels) != x.shape[0]:
                    raise ValueError("labels list must have exactly %s items, but has %s."%(x.shape[0],len(labels)))


        self.gp('set title "%s"'%title)
        if not labels:
            labels = ['s%s'%i for i in range(x.shape[0])]
        if len(x.shape) > 1 and len(x.shape) <= 2:
            i = 0
            for n in range(x.shape[0]):
                self.plots.append(Gnuplot.PlotItems.Data(x[n]*jt,y[n]*jt,title=labels[i],with_=style))
                i += 1
            if multiplot:
                [self.gp.plot(pl) for pl in self.plots]
                self.gp('unset multiplot')
            else:
                self.gp.plot(*tuple(self.plots))
        elif len(x.shape) >2:
                pass
        else:
            #print data
            self.plots.append(Gnuplot.PlotItems.Data(x*jt,y*jt,title=labels[0],with_=style))
            if multiplot:
                [self.gp.plot(pl) for pl in self.plots]
                self.gp('unset multiplot')
            else:
                self.gp.plot(*tuple(self.plots))
        if not self.hold:
            self.plots = []
        return 0
    
    @enqueue
    def lines(self, data, x=[], labels=[],title='',style='lines', multiplot=0):
        '''
        Create a single/multiple line plot from a numpy array or record array.
        
        :Parameters:
            - `data`: must be a list of lists.
            - `x`: x values for the series: list
            - `labels`: is a list of strings to serve as legend labels
            - `style`: plot styles from gnuplot: lines, boxes, points, linespoints, etc.
            - `multiplot`: Whether to make multiple subplots
        '''
        #self.gp('set style %s 1'%style)
        if multiplot:
            sq = numpy.sqrt(len(data))
            ad = 1 if sq%1 >0.5 else 0
            r= numpy.floor(sq);c=numpy.ceil(sq)+ad
            if len(data) == 3:
                r=3;c=1
            self.gp('set multiplot layout %s,%s title "%s"'%(r, c, title))
        else:
            self.gp('set title "%s"'%title)
            
        assert isinstance (data, list)
        data = numpy.array(data)
        
        if len(data.shape) > 1 and len(data.shape) <= 2:
            i = 0
            for row in data:
                if  x== []:
                    x = numpy.arange(len(row))
                if labels:
                    self.plots.append(Gnuplot.PlotItems.Data(x, row,title=labels[i], with_=style))
                else:
                    self.plots.append(Gnuplot.PlotItems.Data(x, row, with_=style))
                i += 1
            if multiplot:
                [self.gp.plot(pl) for pl in self.plots]
                self.gp('unset multiplot')
            else:
                self.gp.plot(*tuple(self.plots))
        elif len(data.shape) >2:
                pass
        else:
#            print data
            if x == [] :
                x = numpy.arange(len(data))
            self.plots.append(Gnuplot.PlotItems.Data(x,data,title=labels[0],with_=style))
            self.gp.plot(*tuple(self.plots))
            if not multiplot:
                self.gp('unset multiplot')
        if not self.hold:
            self.plots = []
        return 0

        
    #~ def histogram(self,data,labels=[],title='',multiplot=0):
        #~ self.Queue.put((self._histogram,(data,labels,title,multiplot)))
    @enqueue  
    def histogram(self,data,labels=[],title='',multiplot=0,**kwargs):
        '''
        Create a single/multiple Histogram plot from a numpy array or record array.
        
        :Parameters:
            - `data`: must be a list of lists.
            - `labels`: is a list of strings to serve as legend labels
            - `multiplot`: Whether to make multiple subplots
        '''
        if multiplot:
            sq = numpy.sqrt(len(data))
            ad = 1 if sq%1 >0.5 else 0
            r= numpy.floor(sq);c=numpy.ceil(sq)+ad
            if len(data) == 3:
                r=3;c=1
            self.gp('set multiplot layout %s,%s title "%s"'%(r, c, title))
        else:
            self.gp('set title "%s"'%title)
        self.gp('set style data boxes')
        
        assert isinstance (data, list)
        data = numpy.array(data)
        if not labels:
            labels = ['Var_%s'%i for i in range(data.shape[0])]
        if len(data.shape) == 2:
            for n,row in enumerate(data):
                m,bins = numpy.histogram(row,normed=True,bins=50)
                d = zip(bins[:-1],m)
                self.plots.append(Gnuplot.PlotItems.Data(d,title=labels[n]))
            
            if multiplot:
                [self.gp.plot(pl) for pl in self.plots]
                self.gp('unset multiplot')
            else:
                self.gp.plot(*tuple(self.plots))

                
        elif len(data.shape) >2:
            pass
        elif len(data.shape) == 1:
            m,bins = numpy.histogram(data,normed=True,bins=50)
            d = zip(bins[:-1],m)
            self.plots.append(Gnuplot.PlotItems.Data(d,title=labels[0]))
            self.gp.plot(*tuple(self.plots))
            if multiplot:
                self.gp('unset multiplot')

        if not self.hold:
            self.plots = []
        return 0


class AltXMLRPCServer(SimpleXMLRPCServer):
    '''
    Subclass of SimpleXMLRPCServer which catches signals at the consoles and terminate the server.
    thanks http://code.activestate.com/recipes/114579-remotely-exit-a-xmlrpc-server-cleanly/
    '''

    finished=False

    def register_signal(self, signum):
        signal.signal(signum, self.signal_handler)

    def signal_handler(self, signum, frame):
        print "Caught signal", signum
        self.shutdown()

    def shutdown(self):
        self.finished=True
        return 1

    def serve_forever(self):
        while not self.finished: 
            self.handle_request()

        
def _start_server(server, persist,hold):
    server.register_instance(RTplot(persist=persist, hold=hold))
    server.register_introspection_functions()
    server.serve_forever()



def rpc_plot(port=0, persist=0, hold=0):
    """
    XML RPC plot server factory function
    returns port if server successfully started or 0
    """
    if port == 0:
        port = 10001
    while 1:
        if port in __ports_used:
            port += 1
            continue
        try:
            server = AltXMLRPCServer(("localhost", port),logRequests=False, allow_none=True)
            server.register_introspection_functions()
            server.register_function(server.shutdown)
            p = Process(target=_start_server, args=(server, persist, hold))
           
            #p = Process(target=_start_twisted_server, args=(port, persist))
            p.daemon = True
            p.start()
            break
        except:         
            port += 1
    port = port
    __ports_used.append(port)
    return port
    

if __name__ == "__main__":
    pass
