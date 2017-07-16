#!/usr/bin/env python Sample Test passing with nose and pytest
import unittest
import numpy as np
from gcode_gen import point


class TestPoint(unittest.TestCase):

    def test_2d(self):
        actual = point.Point(1, 2).arr
        expected = np.asarray((1, 2, 0))
        self.assertTrue(np.allclose(actual, expected))

    def test_3d(self):
        actual = point.Point(1, 2, 3).arr
        expected = np.asarray((1, 2, 3))
        self.assertTrue(np.allclose(actual, expected))


class TestPointList(unittest.TestCase):

    def test_empty(self):
        pl = point.PointList()
        self.assertEqual(pl.arr.shape, (0, 3))

    def test_2d_single(self):
        pl = point.PointList()
        pl.append(point.Point(1, 2))
        actual = pl.arr
        expected = np.asarray(((1, 2, 0), ))
        self.assertTrue(np.allclose(actual, expected))

    def test_2d_multi(self):
        pl = point.PointList()
        pl.append(point.Point(1, 2))
        pl.append(point.Point(3, 4))
        actual = pl.arr
        expected = np.asarray(((1, 2, 0), (3, 4, 0)))
        self.assertTrue(np.allclose(actual, expected))

    def test_3d_single(self):
        pl = point.PointList()
        pl.append(point.Point(1, 2, 3))
        actual = pl.arr
        expected = np.asarray(((1, 2, 3), ))
        self.assertTrue(np.allclose(actual, expected))

    def test_3d_multi(self):
        pl = point.PointList()
        pl.append(point.Point(1, 2, 3))
        pl.append(point.Point(4, 5, 6))
        actual = pl.arr
        expected = np.asarray(((1, 2, 3), (4, 5, 6)))
        self.assertTrue(np.allclose(actual, expected))

    def test_2d_3d_mix(self):
        pl = point.PointList()
        pl.append(point.Point(1, 2))
        pl.append(point.Point(4, 5, 6))
        actual = pl.arr
        expected = np.asarray(((1, 2, 0), (4, 5, 6)))
        self.assertTrue(np.allclose(actual, expected))

    def test_extend_basic(self):
        pl0 = point.PointList()
        pl1 = point.PointList()
        pl0.append(point.Point(1, 2))
        pl0.append(point.Point(4, 5, 6))
        pl1.append(point.Point(7, 8, 9))
        pl1.append(point.Point(10, 11))
        pl1.extend(pl0)
        actual = pl1.arr
        expected = np.asarray(((7, 8, 9), (10, 11, 0), (1, 2, 0), (4, 5, 6), ))

    def test_extend_empty_left(self):
        pl0 = point.PointList()
        pl1 = point.PointList()
        pl0.append(point.Point(1, 2))
        pl0.append(point.Point(4, 5, 6))
        pl1.extend(pl0)
        actual = pl1.arr
        expected = np.asarray(((1, 2, 0), (4, 5, 6)))

    def test_extend_empty_right(self):
        pl0 = point.PointList()
        pl1 = point.PointList()
        pl0.append(point.Point(1, 2))
        pl0.append(point.Point(4, 5, 6))
        pl0.extend(pl1)
        actual = pl0.arr
        expected = np.asarray(((1, 2, 0), (4, 5, 6)))

    def test_pointlist_from_list(self):
        pl = point.pointlist_from_list([[1, 1, 0], [3, 1, 0], [3, 3, 0], [1, 3, 0], ])
        actual = pl.arr
        expected = np.asarray([[1, 1, 0], [3, 1, 0], [3, 3, 0], [1, 3, 0], ])


