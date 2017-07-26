import unittest
import numpy as np
from gcode_gen import assembly
from gcode_gen.tool import Carbide3D_101
from gcode_gen.state import CncState, DEFAULT_START


class TestAssembly(unittest.TestCase):
    def gen_test_tree(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40)
        TASM = assembly.Assembly
        root = TASM(name='root', state=state)
        a = TASM(name='a')
        b = TASM(name='b')
        root += a
        root += b
        c = TASM(name='c')
        d = TASM(name='d')
        e = TASM(name='e')
        f = TASM(name='f')
        g = TASM(name='g')
        b += c
        c += d
        c += e
        c += f
        b += g
        return root

    def test_Assembly(self):
        mt = self.gen_test_tree()
        #
        actual = mt.pos.arr
        expect = DEFAULT_START.arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #


class TestSafeJog(unittest.TestCase):
    def test_get_gcode(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40)
        root = assembly.Assembly(name='root', state=state)
        root += assembly.SafeJog().translate(7, 11)
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        expected = '''G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.50000
'''
        self.assertEqual(actual, expected)

    def test_get_points(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40)
        root = assembly.Assembly(name='root', state=state)
        root += assembly.SafeJog().translate(7, 11)
        pl = root.get_points()
        actual = pl.arr
        expect = np.array(((0, 0, 40),
                           (7, 11, 40),
                           (7, 11, 0.5),
                           ))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

