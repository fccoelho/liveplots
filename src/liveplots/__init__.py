"""liveplots — Real-time live plot server using XML-RPC and Gnuplot."""

from liveplots.monitor import Monitor
from liveplots.plotter import RTplot
from liveplots.server import AltXMLRPCServer, PlotServer, rpc_plot

__version__ = "1.0.0"
__all__ = [
    "Monitor",
    "RTplot",
    "AltXMLRPCServer",
    "PlotServer",
    "rpc_plot",
]
