'''polygon fill library'''
import numpy as np
from .. import iter_util
from .. import number
from .. import point as pt
from .. import poly


class FillEdge(object):
    def __init__(self, p0, p1):
        if p0.x > p1.x:
            self.p0, self.p1 = p1, p0
        else:
            self.p0, self.p1 = p0, p1
        if p0.y > p1.y:
            y_min_pt = p1
            y_max_pt = p0
        else:
            y_min_pt = p0
            y_max_pt = p1
        self.y_max = y_max_pt.y
        self.y_min = y_min_pt.y
        self.x_base = y_min_pt.x
        x_delta = y_min_pt.x - y_max_pt.x
        y_delta = y_min_pt.y - y_max_pt.y
        if number.isclose(y_delta, 0):
            self.x_slope = None
        else:
            self.x_slope = x_delta / y_delta

    def get_x_for_y(self, y):
        return self.x_base + self.x_slope * (y - self.y_min)

    def __str__(self):
        fs = "p0:{} p1:{} y_max:{} y_min:{} x_base:{} x_slope:{}"
        return fs.format(self.p0, self.p1, self.y_max, self.y_min, self.x_base, self.x_slope, )


class FillEdgeTable(list):
    def __init__(self, poly):
        if not poly.is_simple():
            raise ValueError('poly argument must be as simple polygon')
        fill_edges = []
        for edge in poly.get_edges():
            p0, p1 = pt.Point(*edge[0]), pt.Point(*edge[1])
            fe = FillEdge(p0, p1)
            if fe.x_slope is not None:
                fill_edges.append(fe)
        fill_edges = sorted(fill_edges,
                            key=lambda x: x.y_min)
        super().__init__(fill_edges)

    def __str__(self):
        return '\n'.join(map(str, self))


def calc_polygon_fill_vertices(pgon, max_spacing):
    '''Traces out a scan-line path to fill a given polygon with a max spacing between rows
    args:
    polyon to fill
    max spacing between passes '''
    assert isinstance(pgon, poly.SimplePolygon)
    result = pt.PointList()
    bounds = pgon.bounds
    pgon_y_min, pgon_y_max = bounds[1]
    y_step_list = number.calc_steps_with_max_spacing(pgon_y_min, pgon_y_max, max_spacing)
    edge_table = FillEdgeTable(pgon)
    cuts, jogs = [], []
    # [1:-1] because the perimeter trace already handles this
    for y_step in list(y_step_list)[1:-1]:
        active_list = []
        wait_list = []
        for edge in edge_table:
            if edge.y_min <= y_step <= edge.y_max:
                active_list.append(edge)
        active_list = sorted(active_list,
                             key=lambda edge: edge.get_x_for_y(y_step))
        raw_points = []
        for edge in active_list:
            point = pt.Point(edge.get_x_for_y(y_step), y_step)
            raw_points.append(point)
        delete_indices = []
        for idx, ((p0, e0), (p1, e1)) in enumerate(iter_util.pairwise_iter(zip(raw_points, active_list))):
            # when we hit a vertex, two consecutive points are equal
            # drop both points for maxima/minima
            # otherwise, drop 1 point
            if p0 == p1:
                delete_indices.append(idx)
                if number.isclose(p0.y, e0.y_min) and number.isclose(p1.y, e1.y_min):
                    delete_indices.append(idx + 1)
                if number.isclose(p0.y, e0.y_max) and number.isclose(p1.y, e1.y_max):
                    delete_indices.append(idx + 1)
        points = []
        for idx, point in enumerate(raw_points):
            if idx not in delete_indices:
                points.append(point)
        print('*' * 80)
        for p0, e0 in zip(points, active_list):
            print(p0, e0)
        #
        is_cut = True
        for segment in iter_util.pairwise_iter(points):
            if is_cut:
                cuts.append(segment)
            else:
                jogs.append(segment)
            is_cut = not is_cut
    from .plot import plot_poly_and_fill_lines
    plot_poly_and_fill_lines(pgon, cuts, jogs)
    return result


