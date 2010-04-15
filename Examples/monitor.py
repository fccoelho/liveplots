#===============================================================================
# Examples for the filemonitor module
#===============================================================================

import numpy as np
from liveplots.filemonitor import Monitor
from liveplots import xmlrpcserver as xmlrpc
import xmlrpclib
import time


port = xmlrpc.rpc_plot(persist=0)
pserver = xmlrpclib.ServerProxy('http://localhost:%s'%port, allow_none=True)


def action(fpath):
    print "action triggered", fpath
    np.load(fpath)
    pserver.lines(data.tolist(),[],['data'],'')
    

monitor = Monitor('/tmp', ['close_write'], action,debug=1)


data = np.random.normal(0,1,1000)
np.save('/tmp/data.npy',data)
# Wait a little bit to allow for the event to be processed
time.sleep(1)
monitor.stop()
