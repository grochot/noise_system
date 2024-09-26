# encoding: utf-8

# Get module version
from ._metadata import __version__

# Import key items from module
from .time_constants import *
from .timeout import Timeout
from .throttle import Throttle
from .stopwatch import Stopwatch
from .time_incrementer import TimeIncrementer

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())
