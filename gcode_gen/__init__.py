import sys
import logging

log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stdout)
log.addHandler(logHandler)

from . import number
from . import cmd
from . import assembly
from . import scad
from . import machine
from . import cuts
from . import shape
from . import hg_coords
