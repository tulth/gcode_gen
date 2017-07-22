#!/usr/bin/env python
# Sample Test passing with nose and pytest
import unittest
import numpy as np
from gcode_gen.tool import Carbide3D_101
from gcode_gen.state import State, CncState, DEFAULT_START


class TestState(unittest.TestCase):

    def test_create(self):
        state = State(z_safe=40, position=DEFAULT_START)
        self.assertEqual(state['z_safe'], 40)
        actual = state['position'].arr
        expect = DEFAULT_START.arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_let(self):
        state = State(z_safe=45, feed_rate=40)
        self.assertEqual(state['feed_rate'], 40)
        self.assertEqual(state['z_safe'], 45)
        with state.let(feed_rate=15, z_safe=10):
            self.assertEqual(state['feed_rate'], 15)
            self.assertEqual(state['z_safe'], 10)
        self.assertEqual(state['feed_rate'], 40)
        self.assertEqual(state['z_safe'], 45)

    def test_excursion(self):
        state = State(z_safe=45, feed_rate=40)
        self.assertEqual(state['feed_rate'], 40)
        self.assertEqual(state['z_safe'], 45)
        with state.excursion():
            state['z_safe'] = -12
            state['feed_rate'] = 100
            self.assertEqual(state['feed_rate'], 100)
            self.assertEqual(state['z_safe'], -12)
        self.assertEqual(state['feed_rate'], 40)
        self.assertEqual(state['z_safe'], 45)


class TestCncState(unittest.TestCase):

    def test_create(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=40)
        self.assertEqual(state['tool'], tool)
        self.assertEqual(state['z_safe'], 40)
        actual = state['position'].arr
        expect = DEFAULT_START.arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_let(self):
        tool = Carbide3D_101()
        state = CncState(tool=tool, z_safe=45, feed_rate=40)
        self.assertEqual(state['feed_rate'], 40)
        self.assertEqual(state['z_safe'], 45)
        with state.let(feed_rate=15, z_safe=10):
            self.assertEqual(state['feed_rate'], 15)
            self.assertEqual(state['z_safe'], 10)
        self.assertEqual(state['feed_rate'], 40)
        self.assertEqual(state['z_safe'], 45)

