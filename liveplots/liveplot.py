"""
This is an executable script which sets up a live plot monitoring a given file

license: GPL v3 or later
7/28/12
"""

__docformat__ = "restructuredtext en"

import numpy as np
from .filemonitor import Monitor
from . import xmlrpcserver as xmlrpc
from xmlrpc.client import ServerProxy
import time
import argparse

port = xmlrpc.rpc_plot(persist=0)
pserver = ServerProxy('http://0.0.0.0:%s' % port, allow_none=True)


def main(args):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Configure a liveplot daemon for a file')
    parser.add_argument('path', help='file or directory to monitor', type='file', nargs='+', required=True)
    parser.add_argument('-e', '--event', help='Action to be monitored', nargs='+',
                        choices=['create', 'delete', 'close_write', 'close_nowrite', 'access', 'attrib', 'modify'],
                        default='modify')
    parser.add_argument('-a', '--action', help='Visualization action to be performed when event is detected.')

    args = parser.parse_args()
    main(args)
