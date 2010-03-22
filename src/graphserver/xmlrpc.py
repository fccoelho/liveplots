__author__="fccoelho@gmail.com"
__date__ ="$26/02/2009 10:44:29$"
__docformat__ = "restructuredtext en"
import Gnuplot
import numpy
from SimpleXMLRPCServer import SimpleXMLRPCServer
from multiprocessing import Process


__ports_used = []

class RTplot:
    '''
    Real time plotting class based on Gnuplot
    '''
    def __init__(self, persist=0,debug=0):
        self.gp = Gnuplot.Gnuplot(persist = persist, debug=debug)
        self.plots = []

    def clearFig(self):
        '''
        Clears the figure.
        '''
        self.plots = []
        #self.gp.reset()
    def close_plot(self):
        self.gp.close()

    def scatter(self,x,y,labels=[],title='',style='points', jitter = True):
        """
        Makes scatter plots from numpy arrays.
        if x and are multidimensional(lists of lists), multiple scatter plots will be generated, pairing rows.
        
        :Parameters:
            -`x`: list of numbers or list of lists
            -`y`: list of numbers or list of lists
        """
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
                    raise ValueError("Labels list should coinatin exactly 2 elements, but has %s"%len(labels))
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
            self.gp.plot(*tuple(self.plots))
        elif len(x.shape) >2:
                pass
        else:
            #print data
            self.plots.append(Gnuplot.PlotItems.Data(x*jt,y*jt,title=labels[0],with_=style))
            self.gp.plot(*tuple(self.plots))
        
    def lines(self, data, x=None, labels=[],title='',style='lines'):
        '''
        Create a single/multiple line plot from a numpy array or record array.
        
        :Parameters:
            - `data`: must be a list of lists.
            - `x`: x values for the series: list
            - `labels`: is a list of strings to serve as legend labels
            - `style`: plot styles from gnuplot: lines, boxes, points, linespoints, etc.
        '''

        self.gp('set title "%s"'%title)
        assert isinstance (data, list)
        data = numpy.array(data)
        
        if len(data.shape) > 1 and len(data.shape) <= 2:
            i = 0
            for row in data:
                if  x== None:
                    x = numpy.arange(len(row))
                if labels:
                    self.plots.append(Gnuplot.PlotItems.Data(x, row,title=labels[i],with_=style))
                else:
                    self.plots.append(Gnuplot.PlotItems.Data(x, row,with_=style))
                i += 1
            self.gp.plot(*tuple(self.plots))
        elif len(data.shape) >2:
                pass
        else:
#            print data
            if x==None:
                x = numpy.arange(len(data))
            self.plots.append(Gnuplot.PlotItems.Data(x,data,title=labels[0],with_=style))
            self.gp.plot(*tuple(self.plots))



    def histogram(self,data,labels=[],title='',):
        '''
        Create a single/multiple Histogram plot from a numpy array or record array.
        
        :Parameters:
            - `data`: must be a list of lists.
            - `labels`: is a list of strings to serve as legend labels
        '''
        self.gp('set style data boxes')
        self.gp('set title "%s"'%title)
        assert isinstance (data, list)
        data = numpy.array(data)
        if not labels:
            labels = ['Var_%s'%i for i in range(data.shape[0])]
        if len(data.shape) > 1 and len(data.shape) <= 2:
            for n,row in enumerate(data):
                m,bins = numpy.histogram(row,normed=True,bins=50)
                d = zip(bins[:-1],m)
                self.plots.append(Gnuplot.PlotItems.Data(d,title=labels[n]))
            self.gp.plot(*tuple(self.plots))
        elif len(data.shape) >2:
            pass
        else:
            m,bins = numpy.histogram(data,normed=True,bins=50)
            d = zip(bins[:-1],m)
            self.plots.append(Gnuplot.PlotItems.Data(d,title=labels[0]))
            self.gp.plot(*tuple(self.plots))




        
def _start_server(server):
    server.register_instance(RTplot(persist=0))
    server.register_introspection_functions()
    server.serve_forever()


def rpc_plot(port=None):
    """
    XML RPC plot server factory function
    returns port if server successfully started or 0
    """
    if port == None:
        po = 9876
        while 1:
            if po not in __ports_used:break
            po += 1
        port = po
    try:
        server = SimpleXMLRPCServer(("localhost", port),logRequests=False, allow_none=True)
        server.register_introspection_functions()
        p = Process(target=_start_server, args=(server, ))
        p.daemon = True
        p.start()
    except:
        return 0
    __ports_used.append(port)
    return port
    

if __name__ == "__main__":
    pass
