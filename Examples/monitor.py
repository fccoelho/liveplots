from __future__ import absolute_import
from __future__ import print_function
#===============================================================================
# Examples for the filemonitor module
#===============================================================================

import numpy as np
from liveplots.filemonitor import Monitor
from liveplots.xmlrpcserver import PlotServer
import six.moves.xmlrpc_client
import time



pserver = PlotServer()


def action(fpath):
    print("action triggered", fpath)
    np.load(fpath)
    pserver.lines(data.tolist(),[],['data'],'')
    

monitor = Monitor('/tmp', ['close_write'], action,debug=1)


data = np.random.normal(0,1,1000)
np.save('/tmp/data.npy',data)
# Wait a little bit to allow for the event to be processed
time.sleep(1)
monitor.stop()

