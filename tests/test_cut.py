import unittest
import numpy as np
from gcode_gen import assembly
from gcode_gen import cut
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
G0 Z0.00000
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
                           (7, 11, 0),
                           ))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))


class TestUnsafeDrill(unittest.TestCase):
    def test(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, drilling_feed_rate=19)
        root = assembly.Assembly(name='root', state=state)
        root += cut.UnsafeDrill(depth=13).translate(7, 11)
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
        root += cut.Drill(depth=13).translate(7, 11)
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        expected = '''G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.00000
F 20.00000
G1 Z-13.00000
G1 Z0.00000
'''
        self.assertEqual(actual, expected)

    def test_get_gcode_x2(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, drilling_feed_rate=20)
        root = assembly.Assembly(name='root', state=state)
        root += cut.Drill(depth=13).translate(7, 11)
        #
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        expected = '''G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.00000
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
        root += cut.Drill(depth=13).translate(7, 11)
        pl = root.get_points()
        actual = pl.arr
        expect = np.array(((0, 0, 40),
                           (7, 11, 40),
                           (7, 11, 0.0),
                           (7, 11, -13),
                           (7, 11, 0),
                           ))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))


class TestMill(unittest.TestCase):
    def test_get_actions(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, milling_feed_rate=50)
        root = assembly.Assembly(name='root', state=state)
        root += cut.Mill(((0, 0), (17, 19))).translate(7, 11)
        root += assembly.SafeZ()
        al = root.get_actions()
        actual = str(al)
        expect = '''Jog (0.00000, 0.00000, 40.00000)
Jog (7.00000, 11.00000, 40.00000)
Jog (7.00000, 11.00000, 0.00000)
SetMillFeedRate (7.00000, 11.00000, 0.00000) 50.00000
Cut (24.00000, 30.00000, 0.00000)
Jog (24.00000, 30.00000, 40.00000)'''
        self.assertEqual(actual, expect)

    def test_get_gcode(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, milling_feed_rate=50)
        root = assembly.Assembly(name='root', state=state)
        root += cut.Mill(((0, 0), (17, 19))).translate(7, 11)
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl))
        expected = '''G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.00000
F 50.00000
G1 X24.00000 Y30.00000'''
        self.assertEqual(actual, expected)

    def test_get_gcode_x2(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, milling_feed_rate=50)
        root = assembly.Assembly(name='root', state=state)
        root += cut.Mill(((0, 0), (17, 19))).translate(7, 11)
        root += assembly.SafeZ()
        #
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        expected = '''G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.00000
F 50.00000
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
        root += cut.Mill(((0, 0), (17, 19))).translate(7, 11)
        root += assembly.SafeZ()
        pl = root.get_points()
        actual = pl.arr
        expect = np.array(((0, 0, 40),
                           (7, 11, 40),
                           (7, 11, 0),
                           (24, 30, 0),
                           (24, 30, 40),
                           ))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_mills(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, milling_feed_rate=50)
        root = assembly.Assembly(name='root', state=state)
        root += cut.Mill(((0, 0),
                          (-1, 0),
                          (1, 0),
                          (-1, 0), ))
        root.translate(7, 11)
        gcl = root.get_gcode()
        print(root.get_actions())
        actual = '\n'.join(map(str, gcl))
        expected = '''G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.00000
F 50.00000
G1 X6.00000
G1 X8.00000
G1 X6.00000'''
        print(actual)
        self.assertEqual(actual, expected)


test_square = [[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0], ]


class TestPolygon(unittest.TestCase):
    def test_get_gcode(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=None, milling_feed_rate=40)
        root = assembly.Assembly(name='root', state=state)
        root += cut.Polygon(vertices=test_square,
                            depth=1,
                            is_filled=False,
                            cut_style='follow-cut',
                            name='poly',
                            ).translate(7, 11)
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        # print()
        # print(actual)
        expected = '''G0 Z40.00000
G0 X6.00000 Y10.00000
G0 Z0.50000
F 40.00000
G1 Z0.00000
G1 X8.00000
G1 Y12.00000
G1 X6.00000
G1 Y10.00000
G1 Z-0.33333
G1 X8.00000
G1 Y12.00000
G1 X6.00000
G1 Y10.00000
G1 Z-0.66667
G1 X8.00000
G1 Y12.00000
G1 X6.00000
G1 Y10.00000
G1 Z-1.00000
G1 X8.00000
G1 Y12.00000
G1 X6.00000
G1 Y10.00000
'''
        self.assertEqual(actual, expected)

