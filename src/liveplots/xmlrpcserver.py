from __future__ import absolute_import
from __future__ import print_function
from six.moves import range
from six.moves import zip

__author__ = "fccoelho@gmail.com"
__date__ = "$26/02/2009 10:44:29$"
__docformat__ = "restructuredtext en"


import numpy
from six.moves.xmlrpc_server import SimpleXMLRPCServer
from threading import Thread, Lock
from six.moves.queue import Queue
import time
from subprocess import PIPE, Popen
import signal

__ports_used = []

Q = Queue()


def worker():
    while True:
        item = Q.get()
        item[0](*item[1])
        Q.task_done()


def enqueue(f):
    """Decorator that places the call on a queue"""

    def queued(self, *args, **kw):
        Q.put((f, (self,) + args))

    queued.__doc__ = f.__doc__
    queued.__name__ = f.__name__
    return queued


class RTplot():
    '''
    Real time plotting class based on Gnuplot
    '''

    def __init__(self, persist=0, debug=0, **kwargs):
        self.gp = Popen(['gnuplot', '-persist'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        self.plots = []
        self.Queue = Q
        self.persist = persist
        self.hold = 0 if 'hold' not in kwargs else kwargs['hold']
        t = Thread(target=worker, args=())
        t.setDaemon(True)
        t.start()

    def set_hold(self, on):
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
        # self.gp.reset()

    def close_plot(self):
        self.flush_queue()
        if self.persist:
            self.gp.close()
        return 0

    def flush_queue(self):
        self.Queue.join()
        return 0

    @enqueue
    def scatter(self, x, y, labels=[], title='', style='points', jitter=True, multiplot=0):
        """
        Makes scatter plots from numpy arrays.
        if x and are multidimensional(lists of lists), multiple scatter plots will be generated, pairing rows.
        
        :Parameters:
            -`x`: list of numbers or list of lists
            -`y`: list of numbers or list of lists
            -`labels`: list of strings (variable names)
            -`title`: Title of the plot
        """
        #self.gp = Popen(['gnuplot', '-persist'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        assert len(x) == len(y)
        if multiplot:
            sq = numpy.sqrt(len(x))
            ad = 1 if sq % 1 > 0.5 else 0
            r = numpy.floor(sq);
            c = numpy.ceil(sq) + ad
            if len(x) == 3:
                r = 3;
                c = 1
            self.gp.stdin.write(('set multiplot layout {},{} title "{}"\n'.format(r, c, title)).encode())
        else:
            self.gp.stdin.write(('set title "%s"' % title).encode())
        if jitter:
            jt = numpy.random.normal(1, 1e-4, 1)[0]
        else:
            jt = 1
        x = numpy.array(x)
        y = numpy.array(y)

        if x.shape != y.shape:
            raise ValueError("x, %s and y, %s arrays must have the same shape." % (x.shape, y.shape))
        if labels:
            if len(x.shape) == 1:
                if len(labels) != 2:
                    raise ValueError("Labels list should contain exactly 2 elements, but has %s" % len(labels))
            else:
                if len(labels) != x.shape[0]:
                    raise ValueError("labels list must have exactly %s items, but has %s." % (x.shape[0], len(labels)))

        self.gp.stdin.write(('set title "%s"' % title).encode())
        if not labels:
            labels = ['s%s' % i for i in range(x.shape[0])]
        if len(x.shape) > 1 and len(x.shape) <= 2:
            i = 0
            for n in range(x.shape[0]):
                d = zip(x[n]*jt, y[n]*jt)
                self._plot_d(d)
                i += 1
            if multiplot:
                self.gp.stdin.write(b'unset multiplot')

        elif len(x.shape) > 2:
            pass
        else:
            # print data
            d = zip(x*jt, y*jt)
            self._plot_d(d)
            if multiplot:
                self.gp.stdin.write(b'unset multiplot')
        if not self.hold:
            self.plots = []
        return 0

    @enqueue
    def lines(self, data, x=[], labels=[], title='', style='lines', multiplot=0):
        '''
        Create a single/multiple line plot from a numpy array or record array.
        
        :Parameters:
            - `data`: must be a list of lists.
            - `x`: x values for the series: list
            - `labels`: is a list of strings to serve as legend labels
            - `style`: plot styles from gnuplot: lines, boxes, points, linespoints, etc.
            - `multiplot`: Whether to make multiple subplots
        '''
        # self.gp('set style %s 1'%style)
        if multiplot:
            sq = numpy.sqrt(len(data))
            ad = 1 if sq % 1 > 0.5 else 0
            r = numpy.floor(sq);
            c = numpy.ceil(sq) + ad
            if len(data) == 3:
                r = 3;
                c = 1
            self.gp.stdin.write(('set multiplot layout {},{} title "{}"\n'.format(r, c, title)).encode())
        else:
            self.gp.stdin.write(('set title "{}"\n'.format(title)).encode())
        self.gp.stdin.write(b"set style lines\n")
        self.gp.stdin.flush()
        assert isinstance(data, list)
        data = numpy.array(data)

        if len(data.shape) > 1 and len(data.shape) <= 2:
            i = 0
            for row in data:
                if x == []:
                    x = numpy.arange(len(row))
                d = zip(x, row)
                self._plot_d(d)

                i += 1
            if multiplot:
                self.gp.stdin.write(b'unset multiplot\n')

        elif len(data.shape) > 2:
            pass
        else:
            #            print data
            if x == [] or x is None:
                x = numpy.arange(len(data))

            d = zip(x, data)
            self._plot_d(d)
            if not multiplot:
                self.gp.stdin.write(b'unset multiplot\n')
        if not self.hold:
            self.plots = []
        return 0


        # ~ def histogram(self,data,labels=[],title='',multiplot=0):
        # ~ self.Queue.put((self._histogram,(data,labels,title,multiplot)))

    @enqueue
    def histogram(self, data, labels=[], title='', multiplot=0, **kwargs):
        '''
        Create a single/multiple Histogram plot from a numpy array or record array.
        
        :Parameters:
            - `data`: must be a list of lists.
            - `labels`: is a list of strings to serve as legend labels
            - `multiplot`: Whether to make multiple subplots
        '''
        if multiplot:
            sq = numpy.sqrt(len(data))
            ad = 1 if sq % 1 > 0.5 else 0
            r = numpy.floor(sq);
            c = numpy.ceil(sq) + ad
            if len(data) == 3:
                r = 3;
                c = 1
            self.gp.stdin.write(('set multiplot layout %s,%s title "%s"\n' % (r, c, title)).encode())
        else:
            self.gp.stdin.write(('set title "%s"\n' % title).encode())
        self.gp.stdin.write(b'''set style data histograms\n
        set style fill solid border -1\n
        ''')
        self.gp.stdin.flush()
        assert isinstance(data, list)
        data = numpy.array(data)
        if not labels:
            labels = ['Var_%s' % i for i in range(data.shape[0])]
        if len(data.shape) == 2:
            for n, row in enumerate(data):
                m, bins = numpy.histogram(row, normed=True, bins=50)
                d = list(zip(bins[:-1], m))
                self._plot_d(d, label=labels[n], style='boxes')

            if multiplot:
                self.gp.stdin.write(b'unset multiplot\n')
            else:
                pass

        elif len(data.shape) > 2:
            pass
        elif len(data.shape) == 1:
            m, bins = numpy.histogram(data, normed=True, bins=50)
            d = list(zip(bins[:-1], m))
            self._plot_d(d)
            if multiplot:
                self.gp.stdin.write(b'unset multiplot\n')

        if not self.hold:
            self.plots = []
        return 0

    def _plot_d(self, d, label="", style='points'):
        """
        Actually plots the data
        """
        self.gp.stdin.write(("plot '-' title '{}' with {}\n".format(label, style)).encode())
        self.gp.stdin.write(("\n".join(("%f "*len(l))%l for l in d)).encode())
        self.gp.stdin.write(b"\ne\n")
        self.gp.stdin.flush()

class AltXMLRPCServer(SimpleXMLRPCServer):
    '''
    Subclass of SimpleXMLRPCServer which catches signals at the consoles and terminate the server.
    thanks http://code.activestate.com/recipes/114579-remotely-exit-a-xmlrpc-server-cleanly/
    '''

    finished = False

    def register_signal(self, signum):
        signal.signal(signum, self.signal_handler)

    def signal_handler(self, signum, frame):
        print("Caught signal", signum)
        self.shutdown()

    def shutdown(self):
        self.finished = True
        return 1

    def serve_forever(self):
        while not self.finished:
            self.handle_request()


def _start_server(server, persist, hold):
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
            server = AltXMLRPCServer(("localhost", port), logRequests=False, allow_none=True)
            server.register_introspection_functions()
            server.register_function(server.shutdown)
            # server.register_signal(signal.SIGHUP)
            # server.register_signal(signal.SIGINT)
            T = Thread(target=_start_server, args=(server, persist, hold))

            # p = Process(target=_start_twisted_server, args=(port, persist))
            T.daemon = True
            T.start()
            break
        except:
            port += 1
    port = port
    __ports_used.append(port)
    return port


if __name__ == "__main__":
    pass
