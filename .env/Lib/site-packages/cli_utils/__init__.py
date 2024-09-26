# encoding: utf-8

# Get module version
from ._metadata import __version__

class Quit(Exception):
    pass

# Import key items from module

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())
