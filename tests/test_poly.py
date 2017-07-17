#!/usr/bin/env python
# Sample Test passing with nose and pytest
import unittest
import numpy as np
from gcode_gen import point
from gcode_gen import poly
from gcode_gen.debug import DBGP
from math import sqrt

# square 2x2 centered at origin in x/y plane
test_square = [[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0], ]

# square 2x2 centered at origin in x/y plane with an extra collinear point
test_square_colin = [[-1, -1, 0], [0, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0], ]

# square 2x2 centered at origin in x/y plane, but with one vertex lifted off the z=0 plane
test_square_skew = [[-1, -1, 0], [1, -1, 0], [1, 1, 1], [-1, 1, 0], ]

# square squashed down so all points lie along a line
test_all_colin = [[-1, -1, 0], [1, -1, 0], [2, -1, 0], [0, -1, 0], ]


class TestPolygon(unittest.TestCase):

    def test_too_few_vertices(self):
        actual = ""
        try:
            sqr = poly.Polygon(point.PointList_from_list(test_square[0:0]))
        except poly.PolygonException as err:
            actual = str(err)
        expect = "Polygon vertices initializer must have at least 3 vertices"
        self.assertEqual(actual, expect)
        #
        actual = ""
        try:
            sqr = poly.Polygon(point.PointList_from_list(test_square[0:1]))
        except poly.PolygonException as err:
            actual = str(err)
        expect = "Polygon vertices initializer must have at least 3 vertices"
        self.assertEqual(actual, expect)

    def test_get_vertices(self):
        sqr = poly.Polygon(point.PointList_from_list(test_square))
        actual = sqr.get_vertices()
        expect = test_square
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_get_edges(self):
        sqr = poly.Polygon(point.PointList_from_list(test_square))
        actual = sqr.get_edges()
        # expect are the 4 edges
        expect = [[[-1, -1, 0], [1, -1, 0]],
                  [[1, -1, 0], [1, 1, 0]],
                  [[1, 1, 0], [-1, 1, 0]],
                  [[-1, 1, 0], [-1, -1, 0]],
                  ]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_get_corners(self):
        sqr = poly.Polygon(point.PointList_from_list(test_square))
        actual = sqr.get_corners()
        # expect are the 4 corners
        expect = [[[[-1, 1, 0], [-1, -1, 0]], [[-1, -1, 0], [1, -1, 0]]],
                  [[[-1, -1, 0], [1, -1, 0]], [[1, -1, 0], [1, 1, 0]]],
                  [[[1, -1, 0], [1, 1, 0]], [[1, 1, 0], [-1, 1, 0]]],
                  [[[1, 1, 0], [-1, 1, 0]], [[-1, 1, 0], [-1, -1, 0]]],
                  ]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_get_corner_vectors(self):
        sqr = poly.Polygon(point.PointList_from_list(test_square))
        actual = sqr.get_corner_vectors()
        # expect are the 4 corners
        expect = [[[0, -2, 0], [2, 0, 0]],
                  [[2, 0, 0], [0, 2, 0]],
                  [[0, 2, 0], [-2, 0, 0]],
                  [[-2, 0, 0], [0, -2, 0]],
                  ]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_get_corner_vector_crossproducts(self):
        sqr = poly.Polygon(point.PointList_from_list(test_square))
        actual = sqr.get_corner_vector_crossproducts()
        expect = [[0, 0, 4],
                  [0, 0, 4],
                  [0, 0, 4],
                  [0, 0, 4],
                  ]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        sqrc = poly.Polygon(point.PointList_from_list(test_square_colin))
        actual = sqrc.get_corner_vector_crossproducts()
        expect = [[0, 0, 2],
                  [0, 0, 0],
                  [0, 0, 2],
                  [0, 0, 4],
                  [0, 0, 4],
                  ]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_is_coplanar(self):
        sqr = poly.Polygon(point.PointList_from_list(test_square))
        self.assertTrue(sqr.is_coplanar())
        #
        sqrc = poly.Polygon(point.PointList_from_list(test_square_colin))
        self.assertTrue(sqrc.is_coplanar())
        #
        sqr_skew = poly.Polygon(point.PointList_from_list(test_square_skew))
        self.assertFalse(sqr_skew.is_coplanar())
        #
        tp = poly.Polygon(point.PointList_from_list(test_all_colin))
        self.assertTrue(tp.is_coplanar())

    def test_is_all_collinear(self):
        sqr = poly.Polygon(point.PointList_from_list(test_square))
        self.assertFalse(sqr.is_all_collinear())
        #
        sqrc = poly.Polygon(point.PointList_from_list(test_square_colin))
        self.assertFalse(sqrc.is_all_collinear())
        #
        sqr_skew = poly.Polygon(point.PointList_from_list(test_square_skew))
        self.assertFalse(sqr_skew.is_all_collinear())
        #
        tp = poly.Polygon(point.PointList_from_list(test_all_colin))
        self.assertTrue(tp.is_all_collinear())

    # def test_get_orientations(self):
    #     # tp = poly.PolygonCoplanar(point.PointList_from_list(test_square))
    #     # actual = tp.get_orientations()
    #     # print(actual)
    #     # expect = [1, 1, 1, 1]
    #     # self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
    #     #
    #     tp = poly.PolygonCoplanar(point.PointList_from_list(test_square_colin))
    #     actual = tp.get_orientations()
    #     print(actual)
    #     expect = [1, 0, 1, 1, 1]
    #     self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
    #     #


class TestPolygonCoplanar(unittest.TestCase):

    def test_get_normal(self):
        tp = poly.PolygonCoplanar(point.PointList_from_list(test_square))
        actual = tp.get_normal()
        expect = [0, 0, 1]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        tp = poly.PolygonCoplanar(point.PointList_from_list(test_square_colin))
        actual = tp.get_normal()
        expect = [0, 0, 1]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        actual = ""
        try:
            tp = poly.PolygonCoplanar(point.PointList_from_list(test_square_skew))
        except poly.PolygonException as err:
            actual = str(err)
        expect = "PolygonCoplanar vertices must be coplanar"
        self.assertEqual(actual, expect)
        #
        actual = ""
        try:
            tp = poly.PolygonCoplanar(point.PointList_from_list(test_all_colin))
        except poly.PolygonException as err:
            actual = str(err)
        expect = "PolygonCoplanar vertices must not all be collinear"
        self.assertEqual(actual, expect)
        # try rotated square
        tp = poly.PolygonCoplanar(point.PointList_from_list(test_square))
        tp.rotate(np.pi / 4, x=0, y=1, z=0)
        tp.apply_transforms()
        actual = tp.get_normal()
        expect = [sqrt(2) / 2, 0, sqrt(2) / 2]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        # try another rotated square
        tp = poly.PolygonCoplanar(point.PointList_from_list(test_square))
        tp.rotate(np.pi / 2, x=1, y=0, z=0)
        tp.apply_transforms()
        actual = tp.get_normal()
        expect = [0, -1, 0]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

