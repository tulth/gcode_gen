import unittest
from io import StringIO
import contextlib
import pathlib
import tempfile
from gcode_gen import project
from gcode_gen.tool import Carbide3D_101, Carbide3D_102
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
        self.maxDiff = None
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=150, milling_feed_rate=50)
        root = Assembly(name='header', state=state)
        root += Mill(x=17, y=19).translate(7, 11)
        root += project.Footer(name='footer', state=state)
        al = root.get_actions()
        actual = str(al)
        expect = '''Jog (0.00000, 0.00000, 40.00000)
Jog (7.00000, 11.00000, 40.00000)
Jog (7.00000, 11.00000, 0.00000)
SetMillFeedRate (7.00000, 11.00000, 0.00000) 50.00000
Cut (24.00000, 30.00000, 0.00000)
Jog (24.00000, 30.00000, 40.00000)
Jog (0.00000, 0.00000, 40.00000)
StopSpindle (0.00000, 0.00000, 40.00000)'''
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
G0 Z0.00000
F 50.00000
G1 X24.00000 Y30.00000
G0 Z40.00000
G0 X0.00000 Y0.00000
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
        # print(actual)
        expect = '''Home (0.00000, 0.00000, 70.00000)
UnitsMillimeters (0.00000, 0.00000, 70.00000)
MotionAbsolute (0.00000, 0.00000, 70.00000)
SetSpindleSpeed (0.00000, 0.00000, 70.00000) 10000
ActivateSpindleCW (0.00000, 0.00000, 70.00000)
SetFeedRate (0.00000, 0.00000, 70.00000) 50.00000
Jog (0.00000, 0.00000, 40.00000)
Jog (7.00000, 11.00000, 40.00000)
Jog (7.00000, 11.00000, 0.00000)
Cut (24.00000, 30.00000, 0.00000)
Jog (24.00000, 30.00000, 40.00000)
Jog (0.00000, 0.00000, 40.00000)
StopSpindle (0.00000, 0.00000, 40.00000)'''
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
G0 Z0.00000
G1 X24.00000 Y30.00000
G0 Z40.00000
G0 X0.00000 Y0.00000
M5'''
        self.assertEqual(actual, expect)
        #
        gcl = root.get_gcode()
        actual = '\n'.join(map(str, gcl))
        self.assertEqual(actual, expect)

    def test_filename(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=None, milling_feed_rate=50)
        #
        root = project.ToolPass(name='test_file', state=state)
        actual = root.filename
        expect = 'test_file.gcode'
        self.assertEqual(actual, expect)
        #
        root = project.ToolPass(name='test_file', filename='somethingelse', state=state)
        actual = root.filename
        expect = 'somethingelse'
        self.assertEqual(actual, expect)

    def test_gcode_dump(self):
        outfile = StringIO()
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40, feed_rate=None, milling_feed_rate=50)
        root = project.ToolPass(name='file', state=state)
        root += Mill(x=17, y=19).translate(7, 11)
        root.gcode_dump(outfile)
        outfile.seek(0)
        actual = outfile.read()
        expect = '''$H
G21
G90
S 10000
M3
F 50.00000
G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.00000
G1 X24.00000 Y30.00000
G0 Z40.00000
G0 X0.00000 Y0.00000
M5
'''
        self.assertEqual(actual, expect)


class TestProject(unittest.TestCase):
    def test_write_gcode_files(self):
        self.maxDiff = None
        with tempfile.TemporaryDirectory() as tmpdirname:
            filepath = pathlib.Path(tmpdirname) / 'test_write_gcode_files'
            prj = project.Project(name=str(filepath))
            prj.state['z_safe'] = 40
            prj.state['milling_feed_rate'] = 50
            c101_tool = Carbide3D_101()
            prj += c101_tool
            c101pass = prj.last()
            c101pass += Mill(x=17, y=19).translate(7, 11)
            # asm = Assembly()
            # c101pass += asm
            # asm += Mill(x=27, y=29).translate(7, 11)
            c102_tool = Carbide3D_102()
            prj += c102_tool
            c102pass = prj.last()
            c102pass += Mill(x=-13, y=-15).translate(7, 11)
            capturedOutput = StringIO()
            with contextlib.redirect_stdout(capturedOutput):
                prj.write_gcode_files()
                actual = capturedOutput.seek(0)
                actual = capturedOutput.read()
                expect = ('Writing file {}_Carbide3D_101.gcode ...done!'.format(filepath) + '\n' +
                          'Writing file {}_Carbide3D_102.gcode ...done!'.format(filepath) + '\n')
                self.assertEqual(actual, expect)
            expect0 = '''$H
G21
G90
S 10000
M3
F 50.00000
G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.00000
G1 X24.00000 Y30.00000
G0 Z40.00000
G0 X0.00000 Y0.00000
M5
'''
            expect1 = '''$H
G21
G90
S 10000
M3
F 50.00000
G0 Z40.00000
G0 X7.00000 Y11.00000
G0 Z0.00000
G1 X-6.00000 Y-4.00000
G0 Z40.00000
G0 X0.00000 Y0.00000
M5
'''
            for filename, expect in zip(map(lambda x: x.name, prj.children), (expect0, expect1)):
                with open(filename + '.gcode', 'r') as act_file:
                    actual = act_file.read()
                self.assertEqual(actual, expect)
            self.assertEqual(c101pass.state['tool'], c101_tool)
            self.assertEqual(c102pass.state['tool'], c102_tool)
