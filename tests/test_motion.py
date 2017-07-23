import unittest
import numpy as np
from gcode_gen import motion
from gcode_gen.tool import Carbide3D_101
from gcode_gen.state import CncState, DEFAULT_START


class TestMotionTree(unittest.TestCase):
    def gen_test_tree(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40)
        root = motion.MotionTree(name='root', state=state)
        a = motion.MotionTree(name='a')
        b = motion.MotionTree(name='b')
        root += a
        root += b
        c = motion.MotionTree(name='c')
        d = motion.MotionTree(name='d')
        e = motion.MotionTree(name='e')
        f = motion.MotionTree(name='f')
        g = motion.MotionTree(name='g')
        b += c
        c += d
        c += e
        c += f
        b += g
        return root

    def test_MotionTree(self):
        mt = self.gen_test_tree()
        #
        actual = mt.pos.arr
        expect = DEFAULT_START.arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #


class TestSafeJog(unittest.TestCase):
    def test(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40)
        root = motion.MotionTree(name='root', state=state)
        root += motion.SafeJog().translate(7, 11)
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        expected = '''G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.50000
'''
        self.assertEqual(actual, expected)


class TestUnsafeDrill(unittest.TestCase):
    def test(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40)
        root = motion.MotionTree(name='root', state=state)
        root += motion.UnsafeDrill(depth=13).translate(7, 11)
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        expected = '''G1 X7.00000 Y11.00000 Z-13.00000
G1 Z0.00000
'''
        self.assertEqual(actual, expected)


class TestDrill(unittest.TestCase):
    def test(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40)
        root = motion.MotionTree(name='root', state=state)
        root += motion.Drill(depth=13).translate(7, 11)
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        print()
        print(actual)

        expected = '''G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.50000
G1 Z-13.00000
G1 Z0.00000
'''
        self.assertEqual(actual, expected)

