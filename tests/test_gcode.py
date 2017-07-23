import unittest
from gcode_gen import gcode


class TestGcode(unittest.TestCase):

    def test_Home(self):
        self.assertEqual(str(gcode.Home()), "$H")

    def test_Comment(self):
        self.assertEqual(str(gcode.Comment('what!')), "(what!)")

    def test_UnitsInches(self):
        self.assertEqual(str(gcode.UnitsInches()), "G20")

    def test_UnitsMillimeters(self):
        self.assertEqual(str(gcode.UnitsMillimeters()), "G21")

    def test_MotionAbsolute(self):
        self.assertEqual(str(gcode.MotionAbsolute()), "G90")

    def test_SetSpindleSpeed(self):
        self.assertEqual(str(gcode.SetSpindleSpeed(9000)), "S 9000")

    def test_SetFeedRate(self):
        self.assertEqual(str(gcode.SetFeedRate(15)), "F 15.00000")

    def test_ActivateSpindleCW(self):
        self.assertEqual(str(gcode.ActivateSpindleCW()), "M3")

    def test_StopSpindle(self):
        self.assertEqual(str(gcode.StopSpindle()), "M5")

    def test_G0(self):
        self.assertEqual(str(gcode.G0()), "G0")
        self.assertEqual(str(gcode.G0(1, 2, 3)), "G0 X1.00000 Y2.00000 Z3.00000")
        self.assertEqual(str(gcode.G0(1, )), "G0 X1.00000")
        self.assertEqual(str(gcode.G0(y=9)), "G0 Y9.00000")

    def test_G1(self):
        self.assertEqual(str(gcode.G1()), "G1")
        self.assertEqual(str(gcode.G1(1, 2, 3)), "G1 X1.00000 Y2.00000 Z3.00000")
        self.assertEqual(str(gcode.G1(1, )), "G1 X1.00000")
        self.assertEqual(str(gcode.G1(y=9)), "G1 Y9.00000")

    def test_G2(self):
        with self.assertRaises(AssertionError):
            str(gcode.G2())
        self.assertEqual(str(gcode.G2(1, 2, 3, 5)), "G2 X1.00000 Y2.00000 Z3.00000 R5.00000")
        with self.assertRaises(AssertionError):
            str(gcode.G2(1, ))
        with self.assertRaises(AssertionError):
            str(gcode.G2(1, 0.70))
        self.assertEqual(str(gcode.G2(1, r=0.70)), "G2 X1.00000 R0.70000")
        self.assertEqual(str(gcode.G2(r=2, z=1, y=9)), "G2 Y9.00000 Z1.00000 R2.00000")

    def test_G3(self):
        with self.assertRaises(AssertionError):
            str(gcode.G3())
        self.assertEqual(str(gcode.G3(1, 2, 3, 5)), "G3 X1.00000 Y2.00000 Z3.00000 R5.00000")
        with self.assertRaises(AssertionError):
            str(gcode.G3(1, ))
        with self.assertRaises(AssertionError):
            str(gcode.G3(1, 0.70))
        self.assertEqual(str(gcode.G3(1, r=0.70)), "G3 X1.00000 R0.70000")
        self.assertEqual(str(gcode.G3(r=2, z=1, y=9)), "G3 Y9.00000 Z1.00000 R2.00000")
