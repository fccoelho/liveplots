
__author__ = "fccoelho@gmail.com"
__date__ = "$26/02/2009 10:44:29$"
__docformat__ = "restructuredtext en"

import numpy
from xmlrpc.server import SimpleXMLRPCServer
from threading import Thread, Lock
from queue import Queue
from xmlrpc.client import ServerProxy
import copy
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
    Real time plotting class based on Gnuplot.
    Maintains a FIFO queue of plotting calls which are consumed sequentially by a worker thread.
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

        assert len(x) == len(y)
        x = numpy.array(x)
        y = numpy.array(y)
        if jitter:
            jt = numpy.random.normal(1, 1e-4, 1)[0]
        else:
            jt = 1.0

        if x.shape != y.shape:
            raise ValueError("x, %s and y, %s arrays must have the same shape." % (x.shape, y.shape))
        if labels:
            if len(x.shape) == 1:
                if len(labels) != 2:
                    raise ValueError("Labels list should contain exactly 2 elements, but has %s" % len(labels))
            else:
                if len(labels) != x.shape[0]:
                    raise ValueError("labels list must have exactly %s items, but has %s." % (x.shape[0], len(labels)))

        if multiplot:
            sq = numpy.sqrt(len(x))
            ad = 1 if sq % 1 > 0.5 else 0
            r = numpy.floor(sq);
            c = numpy.ceil(sq) + ad
            if len(x) == 3:
                r = 3;
                c = 1
            self.gp.stdin.write(('set multiplot layout {},{} title "{}"\n'.format(r, c, title)).encode())
            single = 1
        else:
            self.gp.stdin.write(('set title "{}"\n'.format(title)).encode())
            single = 0

        self.gp.stdin.write(('set title "{}"\n'.format(title)).encode())
        if not labels:
            labels = ['s%s' % i for i in range(x.shape[0])]
        if len(x.shape) > 1 and len(x.shape) <= 2:
            i = 0
            if not single:
                self.gp.stdin.write(("plot {} with {}\n".format(','.join(["'-' title '{}'".format(l) for l in labels]),
                                                                style)).encode())
            for n in range(x.shape[0]):
                d = zip(x[n] * jt, y[n] * jt)
                l = labels[n]
                self._plot_d(d, single=single)
                i += 1
            if multiplot:
                self.gp.stdin.write(b'unset multiplot\n')

        elif len(x.shape) > 2:
            pass
        else:
            x *= jt;
            y *= jt
            d = zip(x, y)
            if not single:
                self.gp.stdin.write(("plot '-' title '{}' with {}\n".format(labels[0], style)).encode())
            self._plot_d(d, single=single)
            if multiplot:
                self.gp.stdin.write(b'unset multiplot\n')
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
            - `style`: plot styles from gnuplot: lines, boxes, points, linespoints, etc. for each series
            - `multiplot`: Whether to make multiple subplots
        '''
        assert isinstance(data, list)
        try:
            assert isinstance(data[0], list)
        except AssertionError as e:
            print(e, 'Converting data into list of lists')
            data = [data]
        try:
            assert len(data[0]) > 0
        except AssertionError as e:
            print("No data Sent: ", e)
        try:
            data = numpy.array(data, dtype=float)
        except ValueError as e:
            print(data)
            raise e
        if labels == []:
            labels = ['S_{}'.format(i) for i in range(len(data))]
        # if isinstance(style, (str, bytes)):
        #     style = copy.deepcopy([style]*len(labels))
        if multiplot:
            sq = numpy.sqrt(len(data))
            ad = 1 if sq % 1 > 0.5 else 0
            r = numpy.floor(sq);
            c = numpy.ceil(sq) + ad
            if len(data) == 3:
                r = 3
                c = 1
            self.gp.stdin.write(('set multiplot layout {},{} title "{}"\n'.format(r, c, title)).encode())
            if len(data.shape) > 1:
                i = 0
                for row, l in zip(data, labels):
                    if x == []:
                        x = numpy.arange(len(row))
                    d = zip(x, row)
                    self._plot_d(d, label=l, style=style, single=1)
                    i += 1
            else:
                if x == [] or x is None:
                    x = numpy.arange(len(data))

                d = zip(x, data)
                self._plot_d(d, style=style, single=1)

            self.gp.stdin.write(b'unset multiplot\n')
        else:
            self.gp.stdin.write(('set title "{}"\n'.format(title)).encode())
            if len(data.shape) > 1:
                i = 0
                self.gp.stdin.write(("plot {}\n".format(
                    ','.join([" '-' title '{}'  with {}".format(l, style) for l in labels]))).encode())
                for row, l in zip(data, labels):
                    if x == []:
                        x = numpy.arange(len(row))
                    d = zip(x, row)
                    self._plot_d(d, label=l, style=style)
                    i += 1
            else:
                if x == [] or x is None:
                    x = numpy.arange(len(data))

                d = zip(x, data)
                self.gp.stdin.write(("plot '-' with {}\n".format(style)).encode())
                self._plot_d(d, style=style)

        return 0

    @enqueue
    def histogram(self, data, labels=[], title='', multiplot=0, **kwargs):
        '''
        Create a single/multiple Histogram plot from a numpy array or record array.
        
        :Parameters:
            - `data`: must be a list of lists.
            - `labels`: is a list of strings to serve as legend labels
            - `multiplot`: Whether to make multiple subplots
        '''
        self.gp.stdin.write(b'''set style data histograms\n
        set style fill solid border -1\n
        ''')
        self.gp.stdin.flush()
        assert isinstance(data, list)
        data = numpy.array(data)
        if not labels:
            labels = ['Var_{}'.format(i) for i in range(data.shape[0])]

        if multiplot:
            sq = numpy.sqrt(len(data))
            ad = 1 if sq % 1 > 0.5 else 0
            r = numpy.floor(sq);
            c = numpy.ceil(sq) + ad
            if len(data) == 3:
                r = 3;
                c = 1
            self.gp.stdin.write(('set multiplot layout %s,%s title "%s"\n' % (r, c, title)).encode())
            single = 1
        else:
            self.gp.stdin.write(('set title "%s"\n' % title).encode())
            single = 0

        if len(data.shape) == 2:
            if not single:
                self.gp.stdin.write(
                    ("plot {}\n".format(','.join([" '-' title '{}' with boxes".format(l) for l in labels]))).encode())
            for n, row in enumerate(data):
                m, bins = numpy.histogram(row, normed=True, bins=50)
                d = list(zip(bins[:-1], m))
                self._plot_d(d, style='boxes', single=single)

            if multiplot:
                self.gp.stdin.write(b'unset multiplot\n')
            else:
                pass

        elif len(data.shape) > 2:
            pass
        elif len(data.shape) == 1:
            m, bins = numpy.histogram(data, normed=True, bins=50)
            d = list(zip(bins[:-1], m))
            if not single:
                self.gp.stdin.write(("plot '-' title '{}' with boxes\n".format(labels[0])).encode())
            self._plot_d(d, style='boxes', single=single)
            if multiplot:
                self.gp.stdin.write(b'unset multiplot\n')

        if not self.hold:
            self.plots = []
        return 0

    def _plot_d(self, d, label="data", style='lines', single=0):
        """
        Actually plots the data
        """
        if single:
            self.gp.stdin.write(("plot '-' title '{}' with {}\n".format(label, style)).encode())
        try:
            self.gp.stdin.write(("\n".join(("%s " * len(l)) % l for l in d)).encode())
            self.gp.stdin.write(b"\ne\n")
        except BrokenPipeError as exc:
            print("A Error occurred (trying to recover: {}".format(exc))
            self.gp = Popen(['gnuplot', '-persist'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            self.gp.stdin.write(("\n".join(("%s " * len(l)) % l for l in d)).encode())
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
    :param port: port in which to listen for ploting commands. If 0, the first available port above 10000 is chosen
    :param persist: If the plot should be persistent
    :param hold: hold the previous plot when plotting.
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
            server.register_signal(signal.SIGHUP)
            server.register_signal(signal.SIGINT)
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


class PlotServer(ServerProxy):
    def __init__(self, port=0, persist=1):
        port = rpc_plot(port=port, persist=persist)
        super(PlotServer, self).__init__("http://localhost:{}".format(port), allow_none=True)


if __name__ == "__main__":
    import six.moves.xmlrpc_client

    port = rpc_plot(persist=0)
    r_tplot = six.moves.xmlrpc_client.ServerProxy('http://localhost:%s' % port)
    data = [numpy.random.normal(0, 1, 1000).tolist() for i in range(4)]
    r_tplot.lines(data, [], ['a', 'b', 'c', 'd'], 'Test Lines', 'lines', 0)
    r_tplot.close_plot()
    r_tplot.close_plot()
