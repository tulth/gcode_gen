from functools import partial
from . import number
from . import iter_util
from . import point as pt
from . import action
from . import poly
from .assembly import Assembly, SafeJog


class UnsafeDrill(Assembly):
    def kwinit(self, depth, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self.depth = depth

    def get_preorder_actions(self):
        al = action.ActionList()
        al += action.SetDrillFeedRate(self.state)
        points = pt.PointList()
        points.append(pt.Point(0, 0, -self.depth))
        points.append(pt.Point(0, 0, 0))
        points = pt.PointList(self.root_transforms(points.arr))
        cut = partial(action.Cut, state=self.state)
        al += cut(*(points[0].arr))
        al += cut(*(points[1].arr))
        return al


class Drill(Assembly):
    '''drills a hole from z=0 to z=depth
    use .translate() to set the start x/y/z location of the drill action.
    '''
    def kwinit(self, depth, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self += SafeJog()
        self += UnsafeDrill(depth=depth)


class UnsafeMill(Assembly):
    def kwinit(self, x=0, y=0, z=0, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self.dest = pt.Point(x, y, z)

    def get_preorder_actions(self):
        al = action.ActionList()
        al += action.SetMillFeedRate(self.state)
        points = pt.PointList()
        points.append(self.dest)
        points = pt.PointList(self.root_transforms(points.arr))
        cut = partial(action.Cut, state=self.state)
        al += cut(*(points[0].arr))
        return al


class Mill(Assembly):
    '''mills a hole from (0, 0, 0) offset to (x, y, z)
    use .translate() to set the start x/y/z location of the mill action.
    '''
    def kwinit(self, x=0, y=0, z=0, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self += SafeJog()
        self += UnsafeMill()  # move to start point
        self += UnsafeMill(x=x, y=y, z=z)


CUT_STYLES = ('outside-cut',  # compensate for tool diameter for an OUTSIDE cut
              'inside-cut',   # compensate for tool diameter for an INSIDE cut
              'follow-cut',   # no compensation
              )


class UnsafeMillPath(Assembly):
    def kwinit(self,
               vertices,
               name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self.vertices = vertices

    def update_children_preorder(self):
        for vert in self.vertices:
            # print(vert)
            self += UnsafeMill(x=vert[0], y=vert[1], z=vert[2])

    def update_children_postorder(self):
        self.children = []


class Polygon(Assembly):
    '''repeatedly cut (simple) polygon to depth.'''
    def kwinit(self,
               vertices,
               depth,
               cut_style,
               is_filled,
               name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self.depth = depth
        if cut_style not in CUT_STYLES:
            raise TypeError('cut_style must be in {}; given arg {}'.format(CUT_STYLES, cut_style))
        self.cut_style = cut_style
        if not isinstance(is_filled, bool):
            raise TypeError('is_filled must be bool; given arg {}'.format(is_filled))
        self.is_filled = is_filled
        assert not(self.is_filled)
        self.poly = poly.SimplePolygon(vertices)

    def update_children_preorder(self):
        pre_children_len = len(self.children)
        cut_poly = self.get_cut_poly()
        self += SafeJog().translate(x=cut_poly.arr[0][0], y=cut_poly.arr[0][1])
        #
        depth_per_pass = self.state['depth_per_milling_pass']
        z_cut_steps = number.calc_steps_with_max_spacing(0, -self.depth, depth_per_pass)
        verts = list(iter_util.all_plus_first_iter(cut_poly.arr))
        for z_cut_step in z_cut_steps:
            self += UnsafeMillPath(vertices=verts).translate(z=z_cut_step)
        return ()

    def update_children_postorder(self):
        self.children = []

    def get_cut_poly(self):
        tool_dia = self.state['tool'].cut_diameter
        if self.cut_style == 'outside-cut':
            return self.poly.grow(tool_dia)
        elif self.cut_style == 'inside-cut':
            return self.poly.shrink(tool_dia)
        else:
            return self.poly

