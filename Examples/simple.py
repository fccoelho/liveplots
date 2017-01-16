from __future__ import absolute_import
from __future__ import print_function
from numpy import random
from liveplots.xmlrpcserver import PlotServer
import time
from six.moves import range

data = random.normal(0, 1, 1000)
data2 = random.normal(4, 1, 1000)

# setting up a couple of servers

pserver = PlotServer(port=0, persist=1)
pserver2 = PlotServer(port=0, persist=1)

# plotting data. 
# pserver.histogram([data.tolist(),data2.tolist()],['data','data2'],'Two Histograms')
# pserver2.lines([data.tolist(),data2.tolist()],[],['data','data2'],'Two plots')

# multiplot scatter
data = [random.normal(random.randint(0, high=10), 1, size=100).tolist() for i in range(7)]
data2 = [random.normal(random.randint(0, high=10), 1, size=100).tolist() for i in range(7)]
pserver.scatter(data, data2, [], 'Multiplot', 'points', 0, 1)
pserver.flush_queue()
# pserver.shutdown()

# succession of 500 multiplot histograms
t0 = time.time()
for n in range(500):
    d = random.normal(random.randint(0, high=10), 1, size=100)
    d2 = random.normal(random.randint(0, high=10), 1, size=100)
    pserver2.histogram([d.tolist(), d2.tolist()], ['data', 'data2'], 'Two Histograms %s' % n, 1)
print("++> Plot rate: %s plots per second." % (100. / (time.time() - t0)))

# succession of 100 multiplot lines
# ===============================================================================
# t0 = time.time()
# for n in range(100):
#    d = random.normal(random.randint(0, high=10),1,size=100)
#    d2 = random.normal(random.randint(0, high=10),1,size=100)
#    pserver2.lines([d.tolist(),d2.tolist()],[],['data','data2'],'Two Histograms - %s'%n,'lines',1)
# print "++> Plot rate: %s plots per second."%(100./(time.time()-t0))
# ===============================================================================

# wait for the queue to empty
pserver2.flush_queue()
# pserver2.shutdown()
