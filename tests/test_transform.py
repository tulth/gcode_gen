#!/usr/bin/env python
# Sample Test passing with nose and pytest
import unittest
import numpy as np
from gcode_gen import transform, point

# square 2x2 with bottom left corner at 1, 2
test_square = [[1, 2, 0], [3, 2, 0], [3, 4, 0], [1, 4, 0], ]


class TestTransformable(unittest.TestCase):

    def test_translate(self):
        sqr = transform.Transformable(point.PointList_from_list(test_square))
        sqr.translate(-1, -2)
        actual = sqr.arr
        expect = np.asarray(test_square)
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        sqr.apply_transforms()
        actual = sqr.arr
        expect = np.asarray([[0, 0, 0], [2, 0, 0], [2, 2, 0], [0, 2, 0], ])
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        sqr = transform.Transformable(point.PointList_from_list(test_square))
        sqr.translate(1, 2, 3)
        actual = sqr.arr
        expect = np.asarray(test_square)
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        sqr.apply_transforms()
        actual = sqr.arr
        expect = np.asarray([[2, 4, 3], [4, 4, 3], [4, 6, 3], [2, 6, 3], ])
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_scale(self):
        sqr = transform.Transformable(point.PointList_from_list(test_square))
        sqr.scale(2, 0.5)
        actual = sqr.arr
        expect = np.asarray(test_square)
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        sqr.apply_transforms()
        actual = sqr.arr
        expect = np.asarray([[2, 1, 0], [6, 1, 0], [6, 2, 0], [2, 2, 0], ])
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_translate_and_scale(self):
        sqr = transform.Transformable(point.PointList_from_list(test_square))
        sqr.translate(-1, -2)
        sqr.scale(2, 0.5)
        actual = sqr.arr
        expect = np.asarray(test_square)
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        sqr.apply_transforms()
        actual = sqr.arr
        expect = np.asarray([[0, 0, 0], [4, 0, 0], [4, 1, 0], [0, 1, 0], ])
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_rotate(self):
        sqr = transform.Transformable(point.PointList_from_list(test_square))
        sqr.translate(-1, -2)
        sqr.scale(0.5, 0.5)
        sqr.rotate(np.pi / 2)
        actual = sqr.arr
        expect = np.asarray(test_square)
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        sqr.apply_transforms()
        actual = sqr.arr
        expect = np.asarray([[0, 0, 0], [0, 1, 0], [-1, 1, 0], [-1, 0, 0], ])
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        sqr = transform.Transformable(point.PointList_from_list(test_square))
        sqr.translate(-1, -2)
        sqr.scale(0.5, 0.5)
        sqr.rotate(np.pi / 2, x=1, y=0, z=0)
        actual = sqr.arr
        expect = np.asarray(test_square)
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        sqr.apply_transforms()
        actual = sqr.arr
        expect = np.asarray([[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1], ])
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

