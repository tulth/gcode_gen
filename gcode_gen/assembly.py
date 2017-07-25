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

    def has_preorder_actions(self):
        return False

    def has_postorder_actions(self):
        return False

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

    def get_actions(self):
        with self.state.excursion():
            al = action.ActionList()
            skipped_self = False
            for step in self.depth_first_walk():
                if step.is_visit:
                    if skipped_self:
                        if step.is_preorder and step.visited.has_preorder_actions():
                            al.extend(step.visited.get_actions())
                        elif step.is_postorder and step.visited.has_postorder_actions():
                            al.extend(step.visited.get_postorder_actions())
                    else:
                        skipped_self = True
        return al


class TransformableAssembly(Assembly, transform.TransformableMixin):
    @property
    def pos(self):
        return self.state['position']

    @pos.setter
    def pos(self, arg):
        self.state['position'] = arg

    def pos_offset(self, x=None, y=None, z=None):
        self.pos = self.pos.offset(x, y, z)

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


class TransformableAssemblyLeaf(TransformableAssembly):
    def append(self, arg):
        raise NotImplementedError('append is not valid for assembly tree leaf')

    def has_preorder_actions(self):
        return True


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


