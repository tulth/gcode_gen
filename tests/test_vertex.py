#!/usr/bin/env python
# Sample Test passing with nose and pytest
import unittest
import numpy as np
from gcode_gen import vertex


class TestPoint(unittest.TestCase):

    def test_2d(self):
        actual = vertex.Point(1, 2).arr
        expected = np.asarray((1, 2, 0))
        self.assertEqual(actual.tolist(), expected.tolist())

    def test_3d(self):
        actual = vertex.Point(1, 2, 3).arr
        expected = np.asarray((1, 2, 3))
        self.assertEqual(actual.tolist(), expected.tolist())


class TestPointList(unittest.TestCase):

    def test_empty(self):
        pl = vertex.PointList()
        self.assertEqual(pl.arr.shape, (0, 3))

    def test_2d_single(self):
        pl = vertex.PointList()
        pl.append(vertex.Point(1, 2))
        actual = pl.arr
        expected = np.asarray(((1, 2, 0), ))
        self.assertEqual(actual.tolist(), expected.tolist())

    def test_2d_multi(self):
        pl = vertex.PointList()
        pl.append(vertex.Point(1, 2))
        pl.append(vertex.Point(3, 4))
        actual = pl.arr
        expected = np.asarray(((1, 2, 0), (3, 4, 0)))
        self.assertEqual(actual.tolist(), expected.tolist())

    def test_3d_single(self):
        pl = vertex.PointList()
        pl.append(vertex.Point(1, 2, 3))
        actual = pl.arr
        expected = np.asarray(((1, 2, 3), ))
        self.assertEqual(actual.tolist(), expected.tolist())

    def test_3d_multi(self):
        pl = vertex.PointList()
        pl.append(vertex.Point(1, 2, 3))
        pl.append(vertex.Point(4, 5, 6))
        actual = pl.arr
        expected = np.asarray(((1, 2, 3), (4, 5, 6)))
        self.assertEqual(actual.tolist(), expected.tolist())

    def test_2d_3d_mix(self):
        pl = vertex.PointList()
        pl.append(vertex.Point(1, 2))
        pl.append(vertex.Point(4, 5, 6))
        actual = pl.arr
        expected = np.asarray(((1, 2, 0), (4, 5, 6)))
        self.assertEqual(actual.tolist(), expected.tolist())

    def test_extend_basic(self):
        pl0 = vertex.PointList()
        pl1 = vertex.PointList()
        pl0.append(vertex.Point(1, 2))
        pl0.append(vertex.Point(4, 5, 6))
        pl1.append(vertex.Point(7, 8, 9))
        pl1.append(vertex.Point(10, 11))
        pl1.extend(pl0)
        actual = pl1.arr
        expected = np.asarray(((7, 8, 9), (10, 11, 0), (1, 2, 0), (4, 5, 6), ))

    def test_extend_empty_left(self):
        pl0 = vertex.PointList()
        pl1 = vertex.PointList()
        pl0.append(vertex.Point(1, 2))
        pl0.append(vertex.Point(4, 5, 6))
        pl1.extend(pl0)
        actual = pl1.arr
        expected = np.asarray(((1, 2, 0), (4, 5, 6)))

    def test_extend_empty_right(self):
        pl0 = vertex.PointList()
        pl1 = vertex.PointList()
        pl0.append(vertex.Point(1, 2))
        pl0.append(vertex.Point(4, 5, 6))
        pl0.extend(pl1)
        actual = pl0.arr
        expected = np.asarray(((1, 2, 0), (4, 5, 6)))

