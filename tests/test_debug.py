#!/usr/bin/env python Sample Test passing with nose and pytest
import unittest
import io
import sys
from gcode_gen import debug


class TestDebug(unittest.TestCase):

    def test_debug_str(self):
        crazyname = 12
        actual = debug.debug_str(crazyname)
        expect = "crazyname = 12"
        self.assertEqual(actual, expect)
        #
        vertices = ((1, 2), (0, 0), (12, 4))
        actual = debug.debug_str(vertices)
        expect = "vertices = ((1, 2), (0, 0), (12, 4))"
        self.assertEqual(actual, expect)

    def test_debug_print(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        crazyname = 12
        actual = debug.debug_str(crazyname)
        expect = "crazyname = 12"
        sys.stdout = sys.__stdout__
        self.assertEqual(actual, expect)
        #
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        vertices = ((1, 2), (0, 0), (12, 4))
        actual = debug.debug_str(vertices)
        expect = "vertices = ((1, 2), (0, 0), (12, 4))"
        sys.stdout = sys.__stdout__
        self.assertEqual(actual, expect)

