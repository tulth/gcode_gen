#!/usr/bin/env python
# Sample Test passing with nose and pytest
import unittest
import numpy as np
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
            print(fe.p0, fe.p1)
        y_min_last = fet[0].y_min
        for fe in fet[1:]:
            print(y_min_last, fe.y_min, y_min_last <= fe.y_min)
            self.assertTrue(y_min_last <= fe.y_min)
            y_min_last = fe.y_min


class TestFillCalc(unittest.TestCase):
    def test_calc_polygon_fill_vertices0(self):
        test_verts = [[1, 2, 0], [3, 2, 0], [4, 5, 0], [0, 4, 0], ]
        pgon = poly.SimplePolygon(test_verts)
        # from gcode_gen.poly.plot import poly_plot
        # poly_plot(pgon)
        result = fill.calc_polygon_fill_vertices(pgon, max_spacing=0.5)

    def test_calc_polygon_fill_vertices1(self):
        test_verts = [[0, 0, 0],
                      [3, 1, 0],
                      [2, 3, 0],
                      [1, 2, 0],
                      [-1, 3, 0],
                      ]
        pgon = poly.SimplePolygon(test_verts)
        # from gcode_gen.poly.plot import poly_plot
        # poly_plot(pgon)
        result = fill.calc_polygon_fill_vertices(pgon, max_spacing=0.5)

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
        # from gcode_gen.poly.plot import poly_plot
        # poly_plot(pgon)
        result = fill.calc_polygon_fill_vertices(pgon, max_spacing=0.5)

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
        # from gcode_gen.poly.plot import poly_plot
        # poly_plot(pgon)
        result = fill.calc_polygon_fill_vertices(pgon, max_spacing=0.25)

