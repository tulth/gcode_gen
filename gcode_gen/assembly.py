from functools import partial
from collections.abc import MutableSequence
from . import base_types
from . import tree
from . import transform
from .state import CncState
from . import point as pt
from . import action


class Assembly(tree.Tree):
    '''tree of assembly items'''
    def kwinit(self, name=None, parent=None, state=None):
        super().kwinit(name, parent)
        self.state = state
        if state is not None:
            if not isinstance(state, CncState):
                raise TypeError('state must be of type CncState')

    @property
    def pos(self):
        return self.state['position']

    @pos.setter
    def pos(self, arg):
        self.state['position'] = arg

    def pos_offset(self, x=None, y=None, z=None):
        self.pos = self.pos.offset(x, y, z)

    def check_type(self, other):
        assert isinstance(other, Assembly)

    def append(self, arg):
        super().append(arg)
        # arg.state = self.state
        for walk_step in arg.depth_first_walk():
            if walk_step.is_visit and walk_step.is_preorder:
                node = walk_step.visited
                node.state = self.state

    def last(self):
        return self.children[-1]

    def get_gcode(self):
        return self.get_actions().get_gcode()

    def get_points(self):
        return self.get_actions().get_points()

    @property
    def root_transforms(self):
        '''get transforms stacked all the way to the root'''
        result = transform.TransformList()
        for walk_step in self.root_walk():
            if walk_step.is_visit and walk_step.is_preorder:
                if isinstance(walk_step.visited, TransformableAssembly):
                    # extend left
                    result[0:0] = walk_step.visited.transforms
        return result

    def get_actions(self):
        with self.state.excursion():
            al = action.ActionList()
            skipped_self = False
            for step in self.depth_first_walk():
                if step.is_visit and step.is_preorder:
                    if skipped_self:
                        if isinstance(step.visited, TransformableAssemblyLeaf):
                            al.extend(step.visited.get_actions())
                    else:
                        skipped_self = True
        return al


class TransformableAssembly(Assembly, transform.TransformableMixin):
    pass


class TransformableAssemblyLeaf(TransformableAssembly):
    def append(self, arg):
        raise NotImplementedError('append is not valid for assembly tree leaf')


class SafeJog(TransformableAssemblyLeaf):
    def kwinit(self, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)

    def get_actions(self):
        al = action.ActionList()
        points = pt.PointList(((0, 0, self.state['z_margin']), ))
        point = pt.PointList(self.root_transforms(points.arr))[0]
        jog = partial(action.Jog, state=self.state)
        al += jog(x=self.pos.x, y=self.pos.y, z=self.state['z_safe'])
        al += jog(x=point.x, y=point.y, z=self.pos.z)
        al += jog(x=point.x, y=point.y, z=point.z)
        return al


class SafeZ(TransformableAssemblyLeaf):
    def kwinit(self, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)

    def get_actions(self):
        al = action.ActionList()
        points = pt.PointList(((0, 0, self.state['z_margin']), ))
        point = pt.PointList(self.root_transforms(points.arr))[0]
        jog = partial(action.Jog, state=self.state)
        al += jog(x=self.pos.x, y=self.pos.y, z=self.state['z_safe'])
        return al


class UnsafeDrill(TransformableAssemblyLeaf):
    def kwinit(self, depth, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self.depth = depth

    def get_actions(self):
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


class Drill(TransformableAssembly):
    '''drills a hole from z=0 to z=depth
    use .translate() to set the start x/y/z location of the drill action.
    '''
    def kwinit(self, depth, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self += SafeJog()
        self += UnsafeDrill(depth=depth)


class UnsafeMill(TransformableAssemblyLeaf):
    def kwinit(self, x=0, y=0, z=0, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self.dest = pt.Point(x, y, z)

    def get_actions(self):
        al = action.ActionList()
        al += action.SetMillFeedRate(self.state)
        points = pt.PointList()
        points.append(pt.Point(0, 0, 0))
        points.append(self.dest)
        points = pt.PointList(self.root_transforms(points.arr))
        cut = partial(action.Cut, state=self.state)
        al += cut(*(points[0].arr))
        al += cut(*(points[1].arr))
        return al


class Mill(TransformableAssembly):
    '''mills a hole from (0, 0, 0) offset to (x, y, z)
    use .translate() to set the start x/y/z location of the mill action.
    '''
    def kwinit(self, x=0, y=0, z=0, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self += SafeJog()
        self += UnsafeMill()  # move to start point
        self += UnsafeMill(x=x, y=y, z=z)

