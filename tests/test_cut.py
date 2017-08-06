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
        self.maxDiff = None
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, drilling_feed_rate=20)
        root = assembly.Assembly(name='root', state=state)
        root += cut.Drill(depth=9.9).translate(7, 11)
        #
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        expected = '''G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.00000
F 20.00000
G1 Z-0.99000
G1 Z0.00000
G1 Z-1.98000
G1 Z0.00000
G1 Z-2.97000
G1 Z0.00000
G1 Z-3.96000
G1 Z0.00000
G1 Z-4.95000
G1 Z0.00000
G1 Z-5.94000
G1 Z0.00000
G1 Z-6.93000
G1 Z0.00000
G1 Z-7.92000
G1 Z0.00000
G1 Z-8.91000
G1 Z0.00000
G1 Z-9.90000
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
        root += cut.Drill(depth=9).translate(7, 11)
        pl = root.get_points()
        actual = pl.arr
        expect = np.array(((0, 0, 40),
                           (7, 11, 40),
                           (7, 11, 0),
                           (7, 11, -1),
                           (7, 11, 0),
                           (7, 11, -2),
                           (7, 11, 0),
                           (7, 11, -3),
                           (7, 11, 0),
                           (7, 11, -4),
                           (7, 11, 0),
                           (7, 11, -5),
                           (7, 11, 0),
                           (7, 11, -6),
                           (7, 11, 0),
                           (7, 11, -7),
                           (7, 11, 0),
                           (7, 11, -8),
                           (7, 11, 0),
                           (7, 11, -9),
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
        # print(root.get_actions())
        actual = '\n'.join(map(str, gcl))
        expected = '''G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.00000
F 50.00000
G1 X6.00000
G1 X8.00000
G1 X6.00000'''
        # print(actual)
        self.assertEqual(actual, expected)


test_square = [[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0], ]


class TestCutPolygon(unittest.TestCase):
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

    def test_get_gcode2(self):
        self.maxDiff = None
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=None,
                         depth_per_milling_pass=0.25,
                         milling_feed_rate=40)
        root = assembly.Assembly(name='root', state=state)
        verts = np.array(test_square) * 5.3975
        root += cut.Polygon(vertices=verts,
                            depth=1,
                            is_filled=False,
                            cut_style='follow-cut',
                            name='poly',
                            )
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        expected = '''G0 Z40.00000
G0 X-5.39750 Y-5.39750
G0 Z0.50000
F 40.00000
G1 Z0.00000
G1 X5.39750
G1 Y5.39750
G1 X-5.39750
G1 Y-5.39750
G1 Z-0.25000
G1 X5.39750
G1 Y5.39750
G1 X-5.39750
G1 Y-5.39750
G1 Z-0.50000
G1 X5.39750
G1 Y5.39750
G1 X-5.39750
G1 Y-5.39750
G1 Z-0.75000
G1 X5.39750
G1 Y5.39750
G1 X-5.39750
G1 Y-5.39750
G1 Z-1.00000
G1 X5.39750
G1 Y5.39750
G1 X-5.39750
G1 Y-5.39750
'''
        self.assertEqual(actual, expected)

    def test_get_gcode_filled(self):
        self.maxDiff = None
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=None,
                         depth_per_milling_pass=0.25,
                         milling_feed_rate=40)
        root = assembly.Assembly(name='root', state=state)
        verts = np.array(test_square) * 5.3975
        root += cut.Polygon(vertices=verts,
                            depth=1,
                            is_filled=True,
                            cut_style='follow-cut',
                            name='poly',
                            )
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        expected = '''G0 Z40.00000
G0 X-5.39750 Y-2.69875
G0 Z0.50000
F 40.00000
G1 Z0.00000
G1 X5.39750
G1 Y0.00000
G1 X-5.39750
G1 Y2.69875
G1 X5.39750
G1 X-5.39750 Y-5.39750
G1 X5.39750
G1 Y5.39750
G1 X-5.39750
G1 Y-5.39750
G1 Y-2.69875
G1 Z-0.25000
G1 X5.39750
G1 Y0.00000
G1 X-5.39750
G1 Y2.69875
G1 X5.39750
G1 X-5.39750 Y-5.39750
G1 X5.39750
G1 Y5.39750
G1 X-5.39750
G1 Y-5.39750
G1 Y-2.69875
G1 Z-0.50000
G1 X5.39750
G1 Y0.00000
G1 X-5.39750
G1 Y2.69875
G1 X5.39750
G1 X-5.39750 Y-5.39750
G1 X5.39750
G1 Y5.39750
G1 X-5.39750
G1 Y-5.39750
G1 Y-2.69875
G1 Z-0.75000
G1 X5.39750
G1 Y0.00000
G1 X-5.39750
G1 Y2.69875
G1 X5.39750
G1 X-5.39750 Y-5.39750
G1 X5.39750
G1 Y5.39750
G1 X-5.39750
G1 Y-5.39750
G1 Y-2.69875
G1 Z-1.00000
G1 X5.39750
G1 Y0.00000
G1 X-5.39750
G1 Y2.69875
G1 X5.39750
G1 X-5.39750 Y-5.39750
G1 X5.39750
G1 Y5.39750
G1 X-5.39750
G1 Y-5.39750
'''
        self.assertEqual(actual, expected)

    def test_get_gcode_filled_translate(self):
        self.maxDiff = None
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=None,
                         depth_per_milling_pass=0.25,
                         milling_feed_rate=40)
        root = assembly.Assembly(name='root', state=state)
        verts = np.array(test_square) * 5.3975
        root += cut.Polygon(vertices=verts,
                            depth=1,
                            is_filled=True,
                            cut_style='follow-cut',
                            name='poly',
                            ).translate(7, 11)
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        expected = '''G0 Z40.00000
G0 X1.60250 Y8.30125
G0 Z0.50000
F 40.00000
G1 Z0.00000
G1 X12.39750
G1 Y11.00000
G1 X1.60250
G1 Y13.69875
G1 X12.39750
G1 X1.60250 Y5.60250
G1 X12.39750
G1 Y16.39750
G1 X1.60250
G1 Y5.60250
G1 Y8.30125
G1 Z-0.25000
G1 X12.39750
G1 Y11.00000
G1 X1.60250
G1 Y13.69875
G1 X12.39750
G1 X1.60250 Y5.60250
G1 X12.39750
G1 Y16.39750
G1 X1.60250
G1 Y5.60250
G1 Y8.30125
G1 Z-0.50000
G1 X12.39750
G1 Y11.00000
G1 X1.60250
G1 Y13.69875
G1 X12.39750
G1 X1.60250 Y5.60250
G1 X12.39750
G1 Y16.39750
G1 X1.60250
G1 Y5.60250
G1 Y8.30125
G1 Z-0.75000
G1 X12.39750
G1 Y11.00000
G1 X1.60250
G1 Y13.69875
G1 X12.39750
G1 X1.60250 Y5.60250
G1 X12.39750
G1 Y16.39750
G1 X1.60250
G1 Y5.60250
G1 Y8.30125
G1 Z-1.00000
G1 X12.39750
G1 Y11.00000
G1 X1.60250
G1 Y13.69875
G1 X12.39750
G1 X1.60250 Y5.60250
G1 X12.39750
G1 Y16.39750
G1 X1.60250
G1 Y5.60250
'''
        self.assertEqual(actual, expected)

    def test_get_gcode_filled2(self):
        self.maxDiff = None
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=None,
                         milling_overlap=0.842519685039,
                         depth_per_milling_pass=0.5,
                         milling_feed_rate=40)
        root = assembly.Assembly(name='root', state=state)
        verts = verts = [[0, 0, 0],
                         [3, 1, 0],
                         [2, 3, 0],
                         [1, 2, 0],
                         [-1, 3, 0], ]
        root += cut.Polygon(vertices=verts,
                            depth=1,
                            is_filled=True,
                            cut_style='follow-cut',
                            name='poly',
                            )
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl)) + '\n'
        print()
        print(actual)
        expected = '''G0 Z40.00000
G0 X-0.16667 Y0.50000
G0 Z0.50000
F 40.00000
G1 Z0.00000
G1 X1.50000
G0 Z40.00000
G0 X3.00000 Y1.00000
G0 Z0.50000
G1 Z0.00000
G1 X-0.33333
G1 X-0.50000 Y1.50000
G1 X2.75000
G1 X2.50000 Y2.00000
G1 X-0.66667
G1 X-0.83333 Y2.50000
G1 X0.00000
G0 Z40.00000
G0 X1.50000
G0 Z0.50000
G1 Z0.00000
G1 X2.25000
G0 Z40.00000
G0 X0.00000 Y0.00000
G0 Z0.50000
G1 Z0.00000
G1 X3.00000 Y1.00000
G1 X2.00000 Y3.00000
G1 X1.00000 Y2.00000
G1 X-1.00000 Y3.00000
G1 X0.00000 Y0.00000
G0 Z40.00000
G0 X-0.16667 Y0.50000
G0 Z0.00000
G1 Z-0.50000
G1 X1.50000
G0 Z40.00000
G0 X3.00000 Y1.00000
G0 Z0.00000
G1 Z-0.50000
G1 X-0.33333
G1 X-0.50000 Y1.50000
G1 X2.75000
G1 X2.50000 Y2.00000
G1 X-0.66667
G1 X-0.83333 Y2.50000
G1 X0.00000
G0 Z40.00000
G0 X1.50000
G0 Z0.00000
G1 Z-0.50000
G1 X2.25000
G0 Z40.00000
G0 X0.00000 Y0.00000
G0 Z0.00000
G1 Z-0.50000
G1 X3.00000 Y1.00000
G1 X2.00000 Y3.00000
G1 X1.00000 Y2.00000
G1 X-1.00000 Y3.00000
G1 X0.00000 Y0.00000
G0 Z40.00000
G0 X-0.16667 Y0.50000
G0 Z-0.50000
G1 Z-1.00000
G1 X1.50000
G0 Z40.00000
G0 X3.00000 Y1.00000
G0 Z-0.50000
G1 Z-1.00000
G1 X-0.33333
G1 X-0.50000 Y1.50000
G1 X2.75000
G1 X2.50000 Y2.00000
G1 X-0.66667
G1 X-0.83333 Y2.50000
G1 X0.00000
G0 Z40.00000
G0 X1.50000
G0 Z-0.50000
G1 Z-1.00000
G1 X2.25000
G0 Z40.00000
G0 X0.00000 Y0.00000
G0 Z-0.50000
G1 Z-1.00000
G1 X3.00000 Y1.00000
G1 X2.00000 Y3.00000
G1 X1.00000 Y2.00000
G1 X-1.00000 Y3.00000
G1 X0.00000 Y0.00000
'''
        self.assertEqual(actual, expected)


# class TestCutCylinder(unittest.TestCase):
#     def test_get_gcode(self):
#         tool = Carbide3D_101()
#         state = CncState(tool=tool, z_safe=40, feed_rate=None, milling_feed_rate=40)
#         root = assembly.Assembly(name='root', state=state)
#         root += cut.Cylinder(depth=12,
#                              diameter=10,
#                              name='cylinder',
#                              ).translate(7, 11)
#         gcl = root.get_gcode()
#         actual = '\n'.join(map(str, gcl)) + '\n'
#         print()
#         print(actual)
#         expected = '''G0 Z40.00000
# G0 X6.00000 Y10.00000
# G0 Z0.50000
# F 40.00000
# G1 Z0.00000
# G1 X8.00000
# G1 Y12.00000
# G1 X6.00000
# G1 Y10.00000
# G1 Z-0.33333
# G1 X8.00000
# G1 Y12.00000
# G1 X6.00000
# G1 Y10.00000
# G1 Z-0.66667
# G1 X8.00000
# G1 Y12.00000
# G1 X6.00000
# G1 Y10.00000
# G1 Z-1.00000
# G1 X8.00000
# G1 Y12.00000
# G1 X6.00000
# G1 Y10.00000
# '''
#         self.assertEqual(actual, expected)

