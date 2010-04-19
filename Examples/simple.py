from numpy import random
from liveplots import xmlrpcserver as xmlrpc
import xmlrpclib
import time 


data = random.normal(0,1,1000)
data2 = random.normal(4,1,1000)

#setting up a couple of servers
port = xmlrpc.rpc_plot(persist=0)
port2 = xmlrpc.rpc_plot(persist=1) #Persistant plot
print "==> port:",port2
pserver = xmlrpclib.ServerProxy('http://localhost:%s'%port, allow_none=True)
pserver2 = xmlrpclib.ServerProxy('http://localhost:%s'%port2, allow_none=True)

# plotting data. 
# pserver.histogram([data.tolist(),data2.tolist()],['data','data2'],'Two Histograms')
# pserver2.lines([data.tolist(),data2.tolist()],[],['data','data2'],'Two plots')

#succession of 100 multiplot histograms
t0 = time.time()
for n in range(100):
    d = random.normal(random.randint(0, high=10),1,size=100)
    d2 = random.normal(random.randint(0, high=10),1,size=100)
    pserver2.histogram([d.tolist(),d2.tolist()],['data','data2'],'Two Histograms - %s'%n,1)
print "++> Plot rate: %s plots per second."%(100./(time.time()-t0)) 

#succession of 100 multiplot lines
#===============================================================================
# t0 = time.time()
# for n in range(100):
#    d = random.normal(random.randint(0, high=10),1,size=100)
#    d2 = random.normal(random.randint(0, high=10),1,size=100)
#    pserver2.lines([d.tolist(),d2.tolist()],[],['data','data2'],'Two Histograms - %s'%n,'lines',1)
# print "++> Plot rate: %s plots per second."%(100./(time.time()-t0))
#===============================================================================

# wait for the queue to empty
pserver2.flush_queue()
