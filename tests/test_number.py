#!/usr/bin/env python Sample Test passing with nose and pytest
import unittest
import numpy as np
from gcode_gen import number


class TestNumber(unittest.TestCase):

    def test_safe_ceil(self):
        self.assertEqual(number.safe_ceil(3.9999999), 4)
        self.assertEqual(number.safe_ceil(4.00000001), 4)
        self.assertEqual(number.safe_ceil(4.1), 5)

    def test_num2str(self):
        self.assertEqual(number.num2str(3.999999), "4.00000")
        self.assertEqual(number.num2str(4.00000001), "4.00000")

    def test_calc_steps_with_max_spacing(self):
        # check with some canned values and reverses
        actual = number.calc_steps_with_max_spacing(0, 3, 1)
        expect = (0, 1, 2, 3)
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        actual = number.calc_steps_with_max_spacing(3, 0, 1)
        expect = (3, 2, 1, 0)
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        actual = number.calc_steps_with_max_spacing(0, 3.1, 1)
        expect = [0, 0.775, 1.55, 2.325, 3.1]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        actual = number.calc_steps_with_max_spacing(3, -0.1, 1)
        expect = [3, 2.225, 1.45, 0.675, -0.1]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        actual = number.calc_steps_with_max_spacing(0, 3, 1)
        expect = (0, 1, 2, 3.00000001)
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        actual = number.calc_steps_with_max_spacing(3, 0, 1)
        expect = (3.0000001, 2, 1, 0)
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        # check that (max) step is not violated
        step = 1
        #
        diff = np.diff(number.calc_steps_with_max_spacing(0, 3, step))
        self.assertTrue(self._helper_arr_le(diff, step), 'diff: {}\nmax_step:{}'.format(diff, step))
        #
        diff = np.diff(number.calc_steps_with_max_spacing(3, 0, step))
        self.assertTrue(self._helper_arr_le(diff, step), 'diff: {}\nmax_step:{}'.format(diff, step))
        #
        diff = np.diff(number.calc_steps_with_max_spacing(0, 3.1, step))
        self.assertTrue(self._helper_arr_le(diff, step), 'diff: {}\nmax_step:{}'.format(diff, step))
        #
        diff = np.diff(number.calc_steps_with_max_spacing(3, -0.1, step))
        self.assertTrue(self._helper_arr_le(diff, step), 'diff: {}\nmax_step:{}'.format(diff, step))
        #
        diff = np.diff(number.calc_steps_with_max_spacing(0, 3, step))
        self.assertTrue(self._helper_arr_le(diff, step), 'diff: {}\nmax_step:{}'.format(diff, step))
        #
        diff = np.diff(number.calc_steps_with_max_spacing(3, 0, step))
        self.assertTrue(self._helper_arr_le(diff, step), 'diff: {}\nmax_step:{}'.format(diff, step))
        #

    def _helper_arr_le(self, arr, max_val):
        result = True
        for val in arr:
            if val < max_val or number.isclose(val, max_val):
                pass
            else:
                result = False
        return result
