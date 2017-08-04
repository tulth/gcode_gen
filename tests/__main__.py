import unittest
# style
from .test_pycodestyle import *
# debug
from .test_debug import *
# base types
from .test_base_types import *
from .test_tree import *
# numerics
from .test_number import *
from .test_iter import *
from .test_point import *
from .test_transform import *
from .test_poly import *
from .test_poly_fill import *
# gcode / machine
from .test_gcode import *
from .test_state import *
#
from .test_assembly import *
from .test_cut import *
#
from .test_project import *

if __name__ == '__main__':
    unittest.main()
