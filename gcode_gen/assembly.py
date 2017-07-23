from functools import partial
from collections.abc import MutableSequence
from . import base_types
from . import tree
from . import transform
from .state import CncState
from . import point as pt
from .action import ActionList, Jog, Cut, SetDrillFeedRate


class Assembly(tree.Tree):
    '''tree of assembly items'''
    def kwinit(self, name=None, parent=None, state=None):
        super().kwinit(name, parent)
        self.state = state
        if state is not None:
            if not isinstance(state, CncState):
                raise TypeError('state must be of type cncstate')

    @property
    def pos(self):
        return self.state['position']

    @pos.setter
    def pos(self, arg):
        self.state['position'] = arg

    def pos_mv(self, x=None, y=None, z=None):
        xyz = []
        for new_val, old_val in zip((x, y, z), self.pos.arr):
            val = old_val
            if new_val is not None:
                val = new_val
            xyz.append(val)
        self.pos = Point(*xyz)

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
        return self.get_action_list().get_gcode()

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

    def get_action_list(self):
        with self.state.excursion():
            ml = ActionList()
            skipped_self = False
            for step in self.depth_first_walk():
                if step.is_visit and step.is_preorder:
                    if skipped_self:
                        if isinstance(step.visited, TransformableAssemblyLeaf):
                            ml.extend(step.visited.get_action_list())
                    else:
                        skipped_self = True
        return ml


class TransformableAssembly(Assembly, transform.TransformableMixin):
    pass


class TransformableAssemblyLeaf(TransformableAssembly):
    def append(self, arg):
        raise NotImplementedError('append is not valid for assembly tree leaf')


class SafeJog(TransformableAssemblyLeaf):
    def kwinit(self, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)

    def get_action_list(self):
        ml = ActionList()
        points = pt.PointList(((0, 0, self.state['z_margin']), ))
        point = pt.PointList(self.root_transforms(points.arr))[0]
        jog = partial(Jog, state=self.state)
        ml += jog(x=self.pos.x, y=self.pos.y, z=self.state['z_safe'])
        ml += jog(x=point.x, y=point.y, z=self.pos.z)
        ml += jog(x=point.x, y=point.y, z=point.z)
        return ml


class UnsafeDrill(TransformableAssemblyLeaf):
    def kwinit(self, depth, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self.depth = depth

    def get_action_list(self):
        ml = ActionList()
        ml += SetDrillFeedRate(self.state)
        points = pt.PointList()
        points.append(pt.Point(0, 0, -self.depth))
        points.append(pt.Point(0, 0, 0))
        points = pt.PointList(self.root_transforms(points.arr))
        cut = partial(Cut, state=self.state)
        ml += cut(*(points[0].arr))
        ml += cut(*(points[1].arr))
        return ml


class Drill(TransformableAssembly):
    '''drills a hole from z=0 to z=depth
    use .translate() to set the final x/y/z location of the drill action.
    '''
    def kwinit(self, depth, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self += SafeJog()
        self += UnsafeDrill(depth=depth)

