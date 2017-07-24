import unittest
import numpy as np
from gcode_gen import assembly
from gcode_gen.tool import Carbide3D_101
from gcode_gen.state import CncState, DEFAULT_START


class TestAssembly(unittest.TestCase):
    def gen_test_tree(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40)
        root = assembly.Assembly(name='root', state=state)
        a = assembly.Assembly(name='a')
        b = assembly.Assembly(name='b')
        root += a
        root += b
        c = assembly.Assembly(name='c')
        d = assembly.Assembly(name='d')
        e = assembly.Assembly(name='e')
        f = assembly.Assembly(name='f')
        g = assembly.Assembly(name='g')
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


class TestUnsafeDrill(unittest.TestCase):
    def test(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, drilling_feed_rate=19)
        root = assembly.Assembly(name='root', state=state)
        root += assembly.UnsafeDrill(depth=13).translate(7, 11)
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        expected = '''F 19.00000
G1 X7.00000 Y11.00000 Z-13.00000
G1 Z0.00000
'''
        self.assertEqual(actual, expected)


class TestDrill(unittest.TestCase):
    def test_get_gcode(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, drilling_feed_rate=20)
        root = assembly.Assembly(name='root', state=state)
        root += assembly.Drill(depth=13).translate(7, 11)
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        expected = '''G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.50000
F 20.00000
G1 Z-13.00000
G1 Z0.00000
'''
        self.assertEqual(actual, expected)

    def test_get_gcode_x2(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, drilling_feed_rate=20)
        root = assembly.Assembly(name='root', state=state)
        root += assembly.Drill(depth=13).translate(7, 11)
        #
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        expected = '''G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.50000
F 20.00000
G1 Z-13.00000
G1 Z0.00000
'''
        self.assertEqual(actual, expected)
        #
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        self.assertEqual(actual, expected)

    def test_get_points(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40)
        root = assembly.Assembly(name='root', state=state)
        root += assembly.Drill(depth=13).translate(7, 11)
        pl = root.get_points()
        actual = pl.arr
        expect = np.array(((0, 0, 40),
                           (7, 11, 40),
                           (7, 11, 0.5),
                           (7, 11, -13),
                           (7, 11, 0),
                           ))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))


class TestMill(unittest.TestCase):
    def test_get_actions(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, milling_feed_rate=50)
        root = assembly.Assembly(name='root', state=state)
        root += assembly.Mill(x=17, y=19).translate(7, 11)
        root += assembly.SafeZ()
        al = root.get_actions()
        actual = '\n'.join(map(str, al))
        expect = '''Jog (0.00000, 0.00000, 40.00000)
Jog (7.00000, 11.00000, 40.00000)
Jog (7.00000, 11.00000, 0.50000)
SetMillFeedRate (7.00000, 11.00000, 0.50000) 50.00000
Cut (7.00000, 11.00000, 0.00000)
Cut (24.00000, 30.00000, 0.00000)
Jog (24.00000, 30.00000, 40.00000)'''
        self.assertEqual(actual, expect)

    def test_get_gcode(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, milling_feed_rate=50)
        root = assembly.Assembly(name='root', state=state)
        root += assembly.Mill(x=17, y=19).translate(7, 11)
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        expected = '''G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.50000
F 50.00000
G1 Z0.00000
G1 X24.00000 Y30.00000
'''
        self.assertEqual(actual, expected)

    def test_get_gcode_x2(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, milling_feed_rate=50)
        root = assembly.Assembly(name='root', state=state)
        root += assembly.Mill(x=17, y=19).translate(7, 11)
        root += assembly.SafeZ()
        #
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        expected = '''G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.50000
F 50.00000
G1 Z0.00000
G1 X24.00000 Y30.00000
G0 Z40.00000
'''
        self.assertEqual(actual, expected)
        #
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        self.assertEqual(actual, expected)

    def test_get_points(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, milling_feed_rate=50)
        root = assembly.Assembly(name='root', state=state)
        root += assembly.Mill(x=17, y=19).translate(7, 11)
        root += assembly.SafeZ()
        pl = root.get_points()
        actual = pl.arr
        expect = np.array(((0, 0, 40),
                           (7, 11, 40),
                           (7, 11, 0.5),
                           (7, 11, 0),
                           (24, 30, 0),
                           (24, 30, 40),
                           ))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))


