# -*- coding: utf-8 -*-
import pkg_resources

from .message import *
from .channel import *
from .process import *
from .action import *
from .simulation import *
from multipledispatch import dispatch

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = 'unknown'