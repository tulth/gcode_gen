#!/usr/bin/env python Sample Test passing with nose and pytest
import unittest
import numpy as np
from gcode_gen import point


class TestPoint(unittest.TestCase):

    def test_2d(self):
        actual = point.Point(1, 2).arr
        expect = np.asarray((1, 2, 0))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_3d(self):
        actual = point.Point(1, 2, 3).arr
        expect = np.asarray((1, 2, 3))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_offset(self):
        p0 = point.Point(1, 2, 3)
        self.assertIsInstance(p0, point.Point)
        actual = p0.offset(5, 7, 9).arr
        expect = [6, 9, 12]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        p0 = point.Point(1, z=3)
        self.assertIsInstance(p0, point.Point)
        actual = p0.offset(z=7, y=5).arr
        expect = [1, 5, 10]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #

    def test_point_changes(self):
        p0 = point.Point(1, 2)
        p1 = point.Point(1, 2)
        actual = point.changes(p0, p1)
        expect = {}
        self.assertEqual(actual, expect)
        #
        p0 = point.Point(1, 2)
        p1 = point.Point(1, 3)
        actual = point.changes(p0, p1)
        expect = {'y': 3}
        self.assertEqual(actual, expect)
        #
        p0 = point.Point(1, 2, 6)
        p1 = point.Point(1, 2)
        actual = point.changes(p0, p1)
        expect = {'z': 0}
        self.assertEqual(actual, expect)
        #
        p0 = point.Point(1, 2)
        p1 = point.Point(1, 2, 6)
        actual = point.changes(p0, p1)
        expect = {'z': 6}
        self.assertEqual(actual, expect)
        #
        p0 = point.Point(2, 2, 7)
        p1 = point.Point(2.1, 2.1)
        actual = point.changes(p0, p1)
        expect = {'x': 2.1, 'y': 2.1, 'z': 0}
        self.assertEqual(actual, expect)


class TestPointList(unittest.TestCase):

    def test_empty(self):
        pl = point.PointList()
        self.assertEqual(pl.shape, (0, 3))

    def test_2d_single(self):
        pl = point.PointList()
        pl.append(point.Point(1, 2))
        actual = pl.arr
        expect = np.asarray(((1, 2, 0), ))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        actual = pl[0].arr
        expect = np.asarray((1, 2, 0))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        self.assertEqual(pl.shape, (1, 3))
        self.assertEqual(pl[0].arr.shape, (3, ))
        self.assertEqual(len(pl), 1)

    def test_2d_multi(self):
        pl = point.PointList()
        pl.append(point.Point(1, 2))
        pl.append(point.Point(3, 4))
        actual = pl.arr
        expect = np.asarray(((1, 2, 0), (3, 4, 0)))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        self.assertEqual(pl.shape, (2, 3))
        self.assertEqual(len(pl), 2)
        #
        actual = pl[0].arr
        expect = np.asarray((1, 2, 0))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        actual = pl[1].arr
        expect = np.asarray((3, 4, 0))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_3d_single(self):
        pl = point.PointList()
        pl.append(point.Point(1, 2, 3))
        actual = pl.arr
        expect = np.asarray(((1, 2, 3), ))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        self.assertEqual(pl.shape, (1, 3))
        self.assertEqual(pl[0].arr.shape, (3, ))
        self.assertEqual(len(pl), 1)
        #
        actual = pl[0].arr
        expect = np.asarray((1, 2, 3))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        actual = pl[-1].arr
        expect = np.asarray((1, 2, 3))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_3d_multi(self):
        pl = point.PointList()
        pl.append(point.Point(1, 2, 3))
        pl.append(point.Point(4, 5, 6))
        actual = pl.arr
        expect = np.asarray(((1, 2, 3), (4, 5, 6)))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        self.assertEqual(pl.shape, (2, 3))
        self.assertEqual(len(pl), 2)
        #
        actual = pl[0].arr
        expect = np.asarray((1, 2, 3))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        actual = pl[1].arr
        expect = np.asarray((4, 5, 6))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        actual = pl[-1].arr
        expect = np.asarray((4, 5, 6))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_2d_3d_mix(self):
        pl = point.PointList()
        pl.append(point.Point(1, 2))
        pl.append(point.Point(4, 5, 6))
        actual = pl.arr
        expect = np.asarray(((1, 2, 0), (4, 5, 6)))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        self.assertEqual(pl.shape, (2, 3))
        self.assertEqual(len(pl), 2)

    def test_extend_basic(self):
        pl0 = point.PointList()
        pl1 = point.PointList()
        pl0.append(point.Point(1, 2))
        pl0.append(point.Point(4, 5, 6))
        pl1.append(point.Point(7, 8, 9))
        pl1.append(point.Point(10, 11))
        pl1.extend(pl0)
        actual = pl1.arr
        expect = np.asarray(((7, 8, 9), (10, 11, 0), (1, 2, 0), (4, 5, 6), ))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        self.assertEqual(pl1.shape, (4, 3))
        self.assertEqual(len(pl1), 4)

    def test_extend_empty_left(self):
        pl0 = point.PointList()
        pl1 = point.PointList()
        pl0.append(point.Point(1, 2))
        pl0.append(point.Point(4, 5, 6))
        pl1.extend(pl0)
        actual = pl1.arr
        expect = np.asarray(((1, 2, 0), (4, 5, 6)))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_extend_empty_right(self):
        pl0 = point.PointList()
        pl1 = point.PointList()
        pl0.append(point.Point(1, 2))
        pl0.append(point.Point(4, 5, 6))
        pl0.extend(pl1)
        actual = pl0.arr
        expect = np.asarray(((1, 2, 0), (4, 5, 6)))
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    # def test_slice_insert_PointList(self):
    #     pl0 = point.PointList()
    #     pl1 = point.PointList()
    #     pl0.append(point.Point(1, 2, 3))
    #     pl0.append(point.Point(4, 5, 6))
    #     pl1.append(point.Point(7, 8, 9))
    #     pl1.append(point.Point(10, 11, 12))
    #     pl0[:0] = pl1
    #     actual = pl0.arr
    #     expect = np.asarray(((7, 8, 9), (10, 11, 12), (1, 2, 3), (4, 5, 6), ))
    #     self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    # def test_slice_insert_nparr(self):
    #     pl0 = point.PointList()
    #     pl1 = point.PointList()
    #     pl0.append(point.Point(1, 2, 3))
    #     pl0.append(point.Point(4, 5, 6))
    #     pl0[:0] = np.asarray(((7, 8, 9), (10, 11, 12), ))
    #     actual = pl0.arr
    #     expect = np.asarray(((7, 8, 9), (10, 11, 12), (1, 2, 3), (4, 5, 6), ))
    #     self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_PointList_from_list(self):
        pl = point.PointList([[1, 1, 0], [3, 1, 0], [3, 3, 0], [1, 3, 0], ])
        actual = pl.arr
        expect = np.asarray([[1, 1, 0], [3, 1, 0], [3, 3, 0], [1, 3, 0], ])
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_PointList_from_nparr(self):
        lst = [[1, 1, 0], [3, 1, 0], [3, 3, 0], [1, 3, 0], ]
        arr = np.asarray(lst, dtype=np.uint8)
        pl = point.PointList(arr)
        actual = pl.arr
        expect = np.asarray(lst, dtype=np.float64)
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        self.assertEqual(pl.arr.dtype, np.float64)

    def test_PointList_slice(self):
        pl_base = point.PointList([[1, 1, 0], [3, 1, 0], [3, 3, 0], [1, 3, 0], ])
        pl = pl_base[1:3]
        actual = pl.arr
        expect = np.asarray([[3, 1, 0], [3, 3, 0], ])
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))


