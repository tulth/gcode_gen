import unittest
from gcode_gen import project
from gcode_gen.tool import Carbide3D_101
from gcode_gen.state import CncState
from gcode_gen.assembly import Assembly
from gcode_gen.cut import Mill


class TestHeader(unittest.TestCase):
    def test_get_actions(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, milling_feed_rate=50)
        root = project.Header(name='header', state=state)
        al = root.get_actions()
        actual = str(al)
        expect = '''Home (0.00000, 0.00000, 70.00000)
UnitsMillimeters (0.00000, 0.00000, 70.00000)
MotionAbsolute (0.00000, 0.00000, 70.00000)
SetSpindleSpeed (0.00000, 0.00000, 70.00000) 10000
ActivateSpindleCW (0.00000, 0.00000, 70.00000)
SetFeedRate (0.00000, 0.00000, 70.00000) 50.00000'''
        self.assertEqual(actual, expect)

    def test_get_gcode(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, milling_feed_rate=50)
        root = project.Header(name='header', state=state)
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl))
        expect = '''$H
G21
G90
S 10000
M3
F 50.00000'''
        self.assertEqual(actual, expect)


class TestFooter(unittest.TestCase):
    def test_get_actions(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, milling_feed_rate=50)
        root = Assembly(name='header', state=state)
        root += Mill(x=17, y=19).translate(7, 11)
        root += project.Footer(name='footer', state=state)
        al = root.get_actions()
        actual = str(al)
        expect = '''Jog (0.00000, 0.00000, 40.00000)
Jog (7.00000, 11.00000, 40.00000)
Jog (7.00000, 11.00000, 0.50000)
SetMillFeedRate (7.00000, 11.00000, 0.50000) 50.00000
Cut (7.00000, 11.00000, 0.00000)
Cut (24.00000, 30.00000, 0.00000)
Jog (24.00000, 30.00000, 40.00000)
Jog (0.00000, 0.00000, 40.00000)
Jog (0.00000, 0.00000, 40.50000)
StopSpindle (0.00000, 0.00000, 40.50000)'''
        self.assertEqual(actual, expect)

    def test_get_gcode(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, milling_feed_rate=50)
        root = Assembly(name='top', state=state)
        root += Mill(x=17, y=19).translate(7, 11)
        root += project.Footer(name='footer', state=state)
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl))
        expect = '''G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.50000
F 50.00000
G1 Z0.00000
G1 X24.00000 Y30.00000
G0 Z40.00000
G0 X0.00000 Y0.00000
G0 Z40.50000
M5'''
        self.assertEqual(actual, expect)


class TestToolPass(unittest.TestCase):
    def test_get_actions(self):
        self.maxDiff = None
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=None, milling_feed_rate=50)
        root = project.ToolPass(name='file', state=state)
        root += Mill(x=17, y=19).translate(7, 11)
        al = root.get_actions()
        actual = str(al)
        print(actual)
        expect = '''Home (0.00000, 0.00000, 70.00000)
UnitsMillimeters (0.00000, 0.00000, 70.00000)
MotionAbsolute (0.00000, 0.00000, 70.00000)
SetSpindleSpeed (0.00000, 0.00000, 70.00000) 10000
ActivateSpindleCW (0.00000, 0.00000, 70.00000)
SetFeedRate (0.00000, 0.00000, 70.00000) 50.00000
Jog (0.00000, 0.00000, 40.00000)
Jog (7.00000, 11.00000, 40.00000)
Jog (7.00000, 11.00000, 0.50000)
Cut (7.00000, 11.00000, 0.00000)
Cut (24.00000, 30.00000, 0.00000)
Jog (24.00000, 30.00000, 40.00000)
Jog (0.00000, 0.00000, 40.00000)
Jog (0.00000, 0.00000, 40.50000)
StopSpindle (0.00000, 0.00000, 40.50000)'''
        self.assertEqual(actual, expect)

    def test_get_gcode(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=None, milling_feed_rate=50)
        root = project.ToolPass(name='file', state=state)
        root += Mill(x=17, y=19).translate(7, 11)
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl))
        expect = '''$H
G21
G90
S 10000
M3
F 50.00000
G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.50000
G1 Z0.00000
G1 X24.00000 Y30.00000
G0 Z40.00000
G0 X0.00000 Y0.00000
G0 Z40.50000
M5'''
        self.assertEqual(actual, expect)
        #
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl))
        self.assertEqual(actual, expect)
