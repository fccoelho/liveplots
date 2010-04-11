from numpy import random
from graphserver import xmlrpcserver as xmlrpc
import xmlrpclib
import time 


data = random.normal(0,1,1000)
data2 = random.normal(4,1,1000)

#setting up a couple of servers
port = xmlrpc.rpc_plot()
port2 = xmlrpc.rpc_plot(persist=0) #Persistant plot
pserver = xmlrpclib.Server('http://localhost:%s'%port, allow_none=True)
pserver2 = xmlrpclib.Server('http://localhost:%s'%port, allow_none=True)
#plotting data. 
# pserver.histogram([data.tolist(),data2.tolist()],['data','data2'],'Two Histograms')
# pserver2.lines([data.tolist(),data2.tolist()],None,['data','data2'],'Two plots')

#succession of 100 multiplot histograms
for n in range(100):
    d = random.normal(random.randint(0, high=10),1,size=100)
    d2 = random.normal(random.randint(0, high=10),1,size=100)
    pserver2.histogram([d.tolist(),d2.tolist()],['data','data2'],'Two Histograms - %s'%n,1)
    time.sleep(3)