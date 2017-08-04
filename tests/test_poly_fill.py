#!/usr/bin/env python
# Sample Test passing with nose and pytest
import unittest
import numpy as np
from gcode_gen.number import allclose
from gcode_gen import poly
from gcode_gen.poly import fill
from gcode_gen import point as pt


class TestFillEdge(unittest.TestCase):
    def test_fill_edge0(self):
        pt0 = pt.Point(0, 1)
        pt1 = pt.Point(2, 4)
        eb = fill.FillEdge(pt0, pt1)
        self.assertEqual(eb.y_max, 4)
        self.assertEqual(eb.y_min, 1)
        self.assertEqual(eb.x_base, 0)

    def test_fill_edge1(self):
        pt0 = pt.Point(0, 1)
        pt1 = pt.Point(2, -4)
        eb = fill.FillEdge(pt0, pt1)
        self.assertEqual(eb.y_max, 1)
        self.assertEqual(eb.y_min, -4)
        self.assertEqual(eb.x_base, 2)

    def test_fill_edge2(self):
        pt0 = pt.Point(0, 1)
        pt1 = pt.Point(-2, -4)
        eb = fill.FillEdge(pt0, pt1)
        self.assertEqual(eb.y_max, 1)
        self.assertEqual(eb.y_min, -4)
        self.assertEqual(eb.x_base, -2)

    def test_fill_edge3(self):
        pt0 = pt.Point(0, 1)
        pt1 = pt.Point(-2, 5)
        eb = fill.FillEdge(pt0, pt1)
        self.assertEqual(eb.y_max, 5)
        self.assertEqual(eb.y_min, 1)
        self.assertEqual(eb.x_base, 0)
        expect = ('p0:(-2.00000, 5.00000, 0.00000) p1:(0.00000, 1.00000, 0.00000) ' +
                  'y_max:5.0 y_min:1.0 x_base:0.0 x_slope:-0.5')
        actual = str(eb)
        self.assertEqual(expect, actual)


class TestFillEdgeTable(unittest.TestCase):
    def test_fill_edge_table(self):
        test_verts = [[1, 2, 0], [3, 2, 0], [4, 5, 0], [0, 4, 0], ]
        pgon = poly.SimplePolygon(test_verts)
        fet = fill.FillEdgeTable(pgon)
        for fe in fet:
            self.assertTrue(fe.p0.x <= fe.p1.x)
            # print(fe.p0, fe.p1)
        y_min_last = fet[0].y_min
        for fe in fet[1:]:
            # print(y_min_last, fe.y_min, y_min_last <= fe.y_min)
            self.assertTrue(y_min_last <= fe.y_min)
            y_min_last = fe.y_min


class TestFillCalc(unittest.TestCase):
    def test_calc_polygon_fill_vertices0(self):
        test_verts = [[1, 2, 0], [3, 2, 0], [4, 5, 0], [0, 4, 0], ]
        pgon = poly.SimplePolygon(test_verts)
        result = fill.calc_polygon_fill_vertices(pgon, max_spacing=0.5)
        actual = result[0].arr
        expect = np.array(((0.75000, 2.50000, 0.00000),
                           (3.16667, 2.50000, 0.00000),
                           (3.33333, 3.00000, 0.00000),
                           (0.50000, 3.00000, 0.00000),
                           (0.25000, 3.50000, 0.00000),
                           (3.50000, 3.50000, 0.00000),
                           (3.66667, 4.00000, 0.00000),
                           (0.00000, 4.00000, 0.00000),
                           (2.00000, 4.50000, 0.00000),
                           (3.83333, 4.50000, 0.00000), ))
        self.assertTrue(allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        actual = result[1]
        expect = [False, True, True, True, True, True, True, True, False, True]
        self.assertEqual(actual, expect)

    def test_calc_polygon_fill_vertices1(self):
        test_verts = [[0, 0, 0],
                      [3, 1, 0],
                      [2, 3, 0],
                      [1, 2, 0],
                      [-1, 3, 0],
                      ]
        pgon = poly.SimplePolygon(test_verts)
        result = fill.calc_polygon_fill_vertices(pgon, max_spacing=0.5)
        actual = result[0].arr
        expect = np.array(((-0.16667, 0.50000, 0.00000),
                           (1.50000, 0.50000, 0.00000),
                           (3.00000, 1.00000, 0.00000),
                           (-0.33333, 1.00000, 0.00000),
                           (-0.50000, 1.50000, 0.00000),
                           (2.75000, 1.50000, 0.00000),
                           (2.50000, 2.00000, 0.00000),
                           (-0.66667, 2.00000, 0.00000),
                           (-0.83333, 2.50000, 0.00000),
                           (0.00000, 2.50000, 0.00000),
                           (1.50000, 2.50000, 0.00000),
                           (2.25000, 2.50000, 0.00000), ))
        self.assertTrue(allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        actual = result[1]
        expect = [False, True, False, True, True, True, True, True, True, True, False, True]
        self.assertEqual(actual, expect)

    def test_calc_polygon_fill_vertices2(self):
        test_verts = [[0, 0, 0],
                      [6, 0, 0],
                      [5, 3, 0],
                      [4, 1, 0],
                      [2, 2, 0],
                      [1, 4, 0],
                      [0, 3, 0],
                      ]
        pgon = poly.SimplePolygon(test_verts)
        result = fill.calc_polygon_fill_vertices(pgon, max_spacing=0.5)
        actual = result[0].arr
        expect = np.array(((0.00000, 0.50000, 0.00000),
                           (5.83333, 0.50000, 0.00000),
                           (5.66667, 1.00000, 0.00000),
                           (0.00000, 1.00000, 0.00000),
                           (0.00000, 1.50000, 0.00000),
                           (3.00000, 1.50000, 0.00000),
                           (4.25000, 1.50000, 0.00000),
                           (5.50000, 1.50000, 0.00000),
                           (5.33333, 2.00000, 0.00000),
                           (4.50000, 2.00000, 0.00000),
                           (2.00000, 2.00000, 0.00000),
                           (0.00000, 2.00000, 0.00000),
                           (0.00000, 2.50000, 0.00000),
                           (1.75000, 2.50000, 0.00000),
                           (4.75000, 2.50000, 0.00000),
                           (5.16667, 2.50000, 0.00000),
                           (1.50000, 3.00000, 0.00000),
                           (0.00000, 3.00000, 0.00000),
                           (0.50000, 3.50000, 0.00000),
                           (1.25000, 3.50000, 0.00000), ))
        self.assertTrue(allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        actual = result[1]
        expect = [False, True, True, True, True, True, False, True, True, True, False, True, True, True, False, True, False, True, False, True]
        self.assertEqual(actual, expect)

    def test_calc_polygon_fill_vertices3(self):
        test_verts = [[0, 0, 0],
                      [5, 0, 0],
                      [5, 2, 0],
                      [4, 2, 0],
                      [4, 1, 0],
                      [3, 1, 0],
                      [3, 2, 0],
                      [2, 2, 0],
                      [2, 1, 0],
                      [1, 1, 0],
                      [1, 2, 0],
                      [0, 2, 0],
                      ]
        pgon = poly.SimplePolygon(test_verts)
        result = fill.calc_polygon_fill_vertices(pgon, max_spacing=0.25)
        actual = result[0].arr
        expect = np.array(((0.00000, 0.25000, 0.00000),
                           (5.00000, 0.25000, 0.00000),
                           (5.00000, 0.50000, 0.00000),
                           (0.00000, 0.50000, 0.00000),
                           (0.00000, 0.75000, 0.00000),
                           (5.00000, 0.75000, 0.00000),
                           (5.00000, 1.00000, 0.00000),
                           (4.00000, 1.00000, 0.00000),
                           (3.00000, 1.00000, 0.00000),
                           (2.00000, 1.00000, 0.00000),
                           (1.00000, 1.00000, 0.00000),
                           (0.00000, 1.00000, 0.00000),
                           (0.00000, 1.25000, 0.00000),
                           (1.00000, 1.25000, 0.00000),
                           (2.00000, 1.25000, 0.00000),
                           (3.00000, 1.25000, 0.00000),
                           (4.00000, 1.25000, 0.00000),
                           (5.00000, 1.25000, 0.00000),
                           (5.00000, 1.50000, 0.00000),
                           (4.00000, 1.50000, 0.00000),
                           (3.00000, 1.50000, 0.00000),
                           (2.00000, 1.50000, 0.00000),
                           (1.00000, 1.50000, 0.00000),
                           (0.00000, 1.50000, 0.00000),
                           (0.00000, 1.75000, 0.00000),
                           (1.00000, 1.75000, 0.00000),
                           (2.00000, 1.75000, 0.00000),
                           (3.00000, 1.75000, 0.00000),
                           (4.00000, 1.75000, 0.00000),
                           (5.00000, 1.75000, 0.00000), ))
        self.assertTrue(allclose(actual, expect), 'actual: {}\nexpect:{}'.format(actual, expect))
        actual = result[1]
        expect = [False, True, True, True, True, True, True, True, False, True, False, True, True, True, False, True, False, True, True, True, False, True, False, True, True, True, False, True, False, True]
        self.assertEqual(actual, expect)
