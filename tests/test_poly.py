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

square_notched = ((0, 0),
                  (10, 0),
                  (10, 4),
                  (8, 4),
                  (8, 6),
                  (10, 6),
                  (10, 10),
                  (0, 10),
                  )

# botched = not simple
square_botched = ((0, 0),
                  (10, 0),
                  (10, 4),
                  (-2, 4),
                  (-2, 6),
                  (10, 6),
                  (10, 10),
                  (0, 10),
                  )


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
        #
        #
        tp = poly.Polygon(point.PointList_from_list(square_notched))
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
    #     # tp = poly.CoplanarPolygon(point.PointList_from_list(test_square))
    #     # actual = tp.get_orientations()
    #     # print(actual)
    #     # expect = [1, 1, 1, 1]
    #     # self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
    #     #
    #     tp = poly.CoplanarPolygon(point.PointList_from_list(test_square_colin))
    #     actual = tp.get_orientations()
    #     print(actual)
    #     expect = [1, 0, 1, 1, 1]
    #     self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
    #     #


class TestCoplanarPolygon(unittest.TestCase):

    def test_get_normal(self):
        tp = poly.CoplanarPolygon(point.PointList_from_list(test_square))
        actual = tp.get_normal()
        expect = [0, 0, 1]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        tp = poly.CoplanarPolygon(point.PointList_from_list(test_square_colin))
        actual = tp.get_normal()
        expect = [0, 0, 1]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        actual = ""
        try:
            tp = poly.CoplanarPolygon(point.PointList_from_list(test_square_skew))
        except poly.PolygonException as err:
            actual = str(err)
        expect = "CoplanarPolygon vertices must be coplanar"
        self.assertEqual(actual, expect)
        #
        actual = ""
        try:
            tp = poly.CoplanarPolygon(point.PointList_from_list(test_all_colin))
        except poly.PolygonException as err:
            actual = str(err)
        expect = "CoplanarPolygon vertices must not all be collinear"
        self.assertEqual(actual, expect)
        # try rotated square
        tp = poly.CoplanarPolygon(point.PointList_from_list(test_square))
        tp.rotate(np.pi / 4, x=0, y=1, z=0)
        tp.apply_transforms()
        actual = tp.get_normal()
        expect = [sqrt(2) / 2, 0, sqrt(2) / 2]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        # try another rotated square
        tp = poly.CoplanarPolygon(point.PointList_from_list(test_square))
        tp.rotate(np.pi / 2, x=1, y=0, z=0)
        tp.apply_transforms()
        actual = tp.get_normal()
        expect = [0, -1, 0]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        #
        tp = poly.CoplanarPolygon(point.PointList_from_list(square_notched))
        actual = tp.get_normal()
        expect = [0, 0, 1]
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_is_convex(self):
        #
        tp = poly.CoplanarPolygon(point.PointList_from_list(test_square))
        self.assertTrue(tp.is_convex())
        #
        tp = poly.CoplanarPolygon(point.PointList_from_list(square_notched))
        self.assertFalse(tp.is_convex())
        #
        tp = poly.CoplanarPolygon(point.PointList_from_list(square_botched))
        self.assertFalse(tp.is_convex())

    def test_is_simple(self):
        #
        tp = poly.CoplanarPolygon(point.PointList_from_list(test_square))
        self.assertTrue(tp.is_simple())
        #
        tp = poly.CoplanarPolygon(point.PointList_from_list(square_notched))
        self.assertTrue(tp.is_simple())
        #
        tp = poly.CoplanarPolygon(point.PointList_from_list(square_botched))
        self.assertFalse(tp.is_simple())


class TestSimplePolygon(unittest.TestCase):
    def test_shrink_square(self):
        SQR_VERTS = [[0., 0.],
                     [10., 0.],
                     [10., 10.],
                     [0., 10.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).shrink(1)
        actual = tp.arr
        expect = [[1., 1.],
                  [9., 1.],
                  [9., 9.],
                  [1., 9.]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_grow_square(self):
        SQR_VERTS = [[0., 0.],
                     [10., 0.],
                     [10., 10.],
                     [0., 10.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).grow(0.5)
        actual = tp.arr
        expect = [[-0.5, -0.5],
                  [10.5, -0.5],
                  [10.5, 10.5],
                  [-0.5, 10.5]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_shrink_square_rev(self):
        SQR_VERTS = [[0., 0.],
                     [0., 10.],
                     [10., 10.],
                     [10., 0.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).shrink(1)
        actual = tp.arr
        expect = [[1., 1.],
                  [1., 9.],
                  [9., 9.],
                  [9., 1.]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_grow_square_rev(self):
        SQR_VERTS = [[0., 0.],
                     [0., 10.],
                     [10., 10.],
                     [10., 0.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).grow(0.5)
        actual = tp.arr
        expect = [[-0.5, -0.5],
                  [-0.5, 10.5],
                  [10.5, 10.5],
                  [10.5, -0.5]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_shrink_square_collinear(self):
        SQR_VERTS = [[0., 0.],
                     [5., 0.],
                     [10., 0.],
                     [10., 10.],
                     [0., 10.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).shrink(1)
        actual = tp.arr
        expect = [[1., 1.],
                  [5., 1.],
                  [9., 1.],
                  [9., 9.],
                  [1., 9.]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_grow_square_collinear(self):
        SQR_VERTS = [[0., 0.],
                     [5., 0.],
                     [10., 0.],
                     [10., 10.],
                     [0., 10.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).grow(0.5)
        actual = tp.arr
        expect = [[-0.5, -0.5],
                  [5., -0.5],
                  [10.5, -0.5],
                  [10.5, 10.5],
                  [-0.5, 10.5]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_shrink_square_collinear_rev(self):
        SQR_VERTS = [[0., 0.],
                     [0., 10.],
                     [10., 10.],
                     [10., 0.],
                     [5., 0.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).shrink(1)
        actual = tp.arr
        expect = [[1., 1.],
                  [1., 9.],
                  [9., 9.],
                  [9., 1.],
                  [5., 1.]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_grow_square_collinear_rev(self):
        SQR_VERTS = [[0., 0.],
                     [0., 10.],
                     [10., 10.],
                     [10., 0.],
                     [5., 0.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).grow(0.5)
        actual = tp.arr
        expect = [[-0.5, -0.5],
                  [-0.5, 10.5],
                  [10.5, 10.5],
                  [10.5, -0.5],
                  [5., -0.5]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_shrink_hexagon(self):
        HEX_VERTS = [[-4.61880215, 0.],
                     [-2.30940108, -4.],
                     [2.30940108, -4.],
                     [4.61880215, 0.],
                     [2.30940108, 4.],
                     [-2.30940108, 4.]]
        tp = poly.SimplePolygon(point.PointList_from_list(HEX_VERTS)).shrink(1)
        actual = tp.arr
        expect = [[-3.46410162, 0.],
                  [-1.73205081, -3.],
                  [1.73205081, -3.],
                  [3.46410162, 0.],
                  [1.73205081, 3.],
                  [-1.73205081, 3.]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_grow_hexagon(self):
        HEX_VERTS = [[-4.61880215, 0.],
                     [-2.30940108, -4.],
                     [2.30940108, -4.],
                     [4.61880215, 0.],
                     [2.30940108, 4.],
                     [-2.30940108, 4.]]
        tp = poly.SimplePolygon(point.PointList_from_list(HEX_VERTS)).grow(0.5)
        actual = tp.arr
        expect = [[-5.19615242, 0.],
                  [-2.59807621, -4.5],
                  [2.59807621, -4.5],
                  [5.19615242, 0.],
                  [2.59807621, 4.5],
                  [-2.59807621, 4.5]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_shrink_hexagon_rev(self):
        HEX_VERTS = [[-4.61880215, 0.],
                     [-2.30940108, 4.],
                     [2.30940108, 4.],
                     [4.61880215, 0.],
                     [2.30940108, -4.],
                     [-2.30940108, -4.]]
        tp = poly.SimplePolygon(point.PointList_from_list(HEX_VERTS)).shrink(1)
        actual = tp.arr
        expect = [[-3.46410162, 0.],
                  [-1.73205081, 3.],
                  [1.73205081, 3.],
                  [3.46410162, 0.],
                  [1.73205081, -3.],
                  [-1.73205081, -3.]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_grow_hexagon_rev(self):
        HEX_VERTS = [[-4.61880215, 0.],
                     [-2.30940108, 4.],
                     [2.30940108, 4.],
                     [4.61880215, 0.],
                     [2.30940108, -4.],
                     [-2.30940108, -4.]]
        tp = poly.SimplePolygon(point.PointList_from_list(HEX_VERTS)).grow(0.5)
        actual = tp.arr
        expect = [[-5.19615242, 0.],
                  [-2.59807621, 4.5],
                  [2.59807621, 4.5],
                  [5.19615242, 0.],
                  [2.59807621, -4.5],
                  [-2.59807621, -4.5]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_shrink_square_notched(self):
        SQR_VERTS = [[0., 0.],
                     [10., 0.],
                     [10., 4.],
                     [8., 4.],
                     [8., 6.],
                     [10., 6.],
                     [10., 10.],
                     [0., 10.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).shrink(1)
        actual = tp.arr
        expect = [[1., 1.],
                  [9., 1.],
                  [9., 3.],
                  [7., 3.],
                  [7., 7.],
                  [9., 7.],
                  [9., 9.],
                  [1., 9.]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_grow_square_notched(self):
        SQR_VERTS = [[0., 0.],
                     [10., 0.],
                     [10., 4.],
                     [8., 4.],
                     [8., 6.],
                     [10., 6.],
                     [10., 10.],
                     [0., 10.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).grow(0.5)
        actual = tp.arr
        expect = [[-0.5, -0.5],
                  [10.5, -0.5],
                  [10.5, 4.5],
                  [8.5, 4.5],
                  [8.5, 5.5],
                  [10.5, 5.5],
                  [10.5, 10.5],
                  [-0.5, 10.5]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_shrink_square_notched_rev(self):
        SQR_VERTS = [[0., 0.],
                     [0., 10.],
                     [10., 10.],
                     [10., 6.],
                     [8., 6.],
                     [8., 4.],
                     [10., 4.],
                     [10., 0.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).shrink(1)
        actual = tp.arr
        expect = [[1., 1.],
                  [1., 9.],
                  [9., 9.],
                  [9., 7.],
                  [7., 7.],
                  [7., 3.],
                  [9., 3.],
                  [9., 1.]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_grow_square_notched_rev(self):
        SQR_VERTS = [[0., 0.],
                     [0., 10.],
                     [10., 10.],
                     [10., 6.],
                     [8., 6.],
                     [8., 4.],
                     [10., 4.],
                     [10., 0.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).grow(0.5)
        actual = tp.arr
        expect = [[-0.5, -0.5],
                  [-0.5, 10.5],
                  [10.5, 10.5],
                  [10.5, 5.5],
                  [8.5, 5.5],
                  [8.5, 4.5],
                  [10.5, 4.5],
                  [10.5, -0.5]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_shrink_square_smashed(self):
        SQR_VERTS = [[0., 0.],
                     [10., 0.],
                     [4., 4.],
                     [0., 10.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).shrink(1)
        actual = tp.arr
        expect = [[1., 1.],
                  [6.69722436, 1.],
                  [3.27888974, 3.27888974],
                  [1., 6.69722436]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_grow_square_smashed(self):
        SQR_VERTS = [[0., 0.],
                     [10., 0.],
                     [4., 4.],
                     [0., 10.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).grow(0.5)
        actual = tp.arr
        expect = [[-0.5, -0.5],
                  [11.65138782, -0.5],
                  [4.36055513, 4.36055513],
                  [-0.5, 11.65138782]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_shrink_square_smashed_rev(self):
        SQR_VERTS = [[0., 0.],
                     [0., 10.],
                     [4., 4.],
                     [10., 0.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).shrink(1)
        actual = tp.arr
        expect = [[1., 1.],
                  [1., 6.69722436],
                  [3.27888974, 3.27888974],
                  [6.69722436, 1.]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_grow_square_smashed_rev(self):
        SQR_VERTS = [[0., 0.],
                     [0., 10.],
                     [4., 4.],
                     [10., 0.]]
        tp = poly.SimplePolygon(point.PointList_from_list(SQR_VERTS)).grow(0.5)
        actual = tp.arr
        expect = [[-0.5, -0.5],
                  [-0.5, 11.65138782],
                  [4.36055513, 4.36055513],
                  [11.65138782, -0.5]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_shrink_hexagon_smashed(self):
        HEX_VERTS = [[-4.61880215, 0.],
                     [-2.30940108, -4.],
                     [2.30940108, -4.],
                     [0., 0.],
                     [2.30940108, 4.],
                     [-2.30940108, 4.]]
        tp = poly.SimplePolygon(point.PointList_from_list(HEX_VERTS)).shrink(1)
        actual = tp.arr
        expect = [[-3.46410162, 0.],
                  [-1.73205081, -3.],
                  [0.57735027, -3.],
                  [-1.15470054, 0.],
                  [0.57735027, 3.],
                  [-1.73205081, 3.]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_grow_hexagon_smashed(self):
        HEX_VERTS = [[-4.61880215, 0.],
                     [-2.30940108, -4.],
                     [2.30940108, -4.],
                     [0., 0.],
                     [2.30940108, 4.],
                     [-2.30940108, 4.]]
        tp = poly.SimplePolygon(point.PointList_from_list(HEX_VERTS)).grow(0.5)
        actual = tp.arr
        expect = [[-5.19615242, 0.],
                  [-2.59807621, -4.5],
                  [3.17542648, -4.5],
                  [0.57735027, 0.],
                  [3.17542648, 4.5],
                  [-2.59807621, 4.5]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_shrink_hexagon_smashed_rev(self):
        HEX_VERTS = [[-4.61880215, 0.],
                     [-2.30940108, 4.],
                     [2.30940108, 4.],
                     [0., 0.],
                     [2.30940108, -4.],
                     [-2.30940108, -4.]]
        tp = poly.SimplePolygon(point.PointList_from_list(HEX_VERTS)).shrink(1)
        actual = tp.arr
        expect = [[-3.46410162, 0.],
                  [-1.73205081, 3.],
                  [0.57735027, 3.],
                  [-1.15470054, 0.],
                  [0.57735027, -3.],
                  [-1.73205081, -3.]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_grow_hexagon_smashed_rev(self):
        HEX_VERTS = [[-4.61880215, 0.],
                     [-2.30940108, 4.],
                     [2.30940108, 4.],
                     [0., 0.],
                     [2.30940108, -4.],
                     [-2.30940108, -4.]]
        tp = poly.SimplePolygon(point.PointList_from_list(HEX_VERTS)).grow(0.5)
        actual = tp.arr
        expect = [[-5.19615242, 0.],
                  [-2.59807621, 4.5],
                  [3.17542648, 4.5],
                  [0.57735027, 0.],
                  [3.17542648, -4.5],
                  [-2.59807621, -4.5]]
        expect = point.PointList_from_list(expect).arr
        self.assertTrue(np.allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))

    def test_invalid_relay_outline(self):
        TST_VERTS = [[30.8737, 1.5875],
                     [40.5257, 1.5875],
                     [40.5257, 25.2095],
                     [26.4287, 25.2095],
                     [26.4287, 22.9235],
                     [24.8412, 24.511],
                     [26.4287, 22.9235],
                     [11.9507, 22.9235],
                     [11.9507, 6.5405],
                     [30.8737, 6.5405],
                     [29.2862, 4.953],
                     [30.8737, 6.5405]]
        actual = ""
        try:
            tp = poly.SimplePolygon(point.PointList_from_list(TST_VERTS))
        except poly.PolygonException as err:
            actual = str(err)
        expect = "SimplePolygon vertices must form a simple polygon's mathematical definition"
        self.assertEqual(actual, expect)
