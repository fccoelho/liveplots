from numpy import random
from graphserver import xmlrpc
import xmlrpclib
import time 


data = random.normal(0,1,1000)
data2 = random.normal(4,1,1000)

#setting up a couple of servers
port = xmlrpc.rpc_plot()
port2 = xmlrpc.rpc_plot()
pserver = xmlrpclib.ServerProxy('http://localhost:%s'%port, allow_none=True)
pserver2 = xmlrpclib.ServerProxy('http://localhost:%s'%port2, allow_none=True)
#plotting data. 
pserver.histogram([data.tolist(),data2.tolist()],['data','data2'],'Two Histograms')
pserver2.lines([data.tolist(),data2.tolist()],None,['data','data2'],'Two plots')

time.sleep(10)