from functools import partial
from collections.abc import MutableSequence
from . import base_types
from . import tree
from . import transform
from .state import CncState
from . import point as pt
from . import action


class Assembly(tree.Tree, transform.TransformableMixin):
    '''tree of assembly items'''
    def __init__(self, name=None, parent=None, state=None):
        super().__init__(name=name, parent=parent)
        if state is not None:
            if not isinstance(state, CncState):
                raise TypeError('state must be of type CncState')
        self._state = state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        for child in self.children:
            child.state = self.state

    def check_type(self, other):
        assert isinstance(other, Assembly)

    def append(self, arg):
        super().append(arg)
        arg.state = self.state

    def last(self):
        return self.children[-1]

    def get_gcode(self):
        return self.get_actions().get_gcode()

    def get_points(self):
        return self.get_actions().get_points()

    def update_children_preorder(self):
        pass

    def get_preorder_actions(self):
        return ()

    def get_postorder_actions(self):
        return ()

    def update_children_postorder(self):
        pass

    def get_actions(self):
        with self.state.excursion():
            al = action.ActionList()
            for step in self.depth_first_walk():
                if step.is_visit:
                    if step.is_preorder:
                        step.visited.update_children_preorder()
                        al.extend(step.visited.get_preorder_actions())
                    elif step.is_postorder:
                        al.extend(step.visited.get_postorder_actions())
                        step.visited.update_children_postorder()
        return al

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
                if isinstance(walk_step.visited, Assembly):
                    # extend left
                    result[0:0] = walk_step.visited.transforms
        return result


class SafeJog(Assembly):
    def __init__(self, name=None, parent=None, state=None):
        super().__init__(name=name, parent=parent, state=state)

    def get_preorder_actions(self):
        al = action.ActionList()
        points = pt.PointList(((0, 0, self.state['z_margin']), ))
        point = pt.PointList(self.root_transforms(points.arr))[0]
        jog = partial(action.Jog, state=self.state)
        al += jog(x=self.pos.x, y=self.pos.y, z=self.state['z_safe'])
        al += jog(x=point.x, y=point.y, z=self.pos.z)
        al += jog(x=point.x, y=point.y, z=point.z)
        return al


class SafeZ(Assembly):
    def __init__(self, name=None, parent=None, state=None):
        super().__init__(name=name, parent=parent, state=state)

    def get_preorder_actions(self):
        al = action.ActionList()
        points = pt.PointList(((0, 0, self.state['z_margin']), ))
        point = pt.PointList(self.root_transforms(points.arr))[0]
        jog = partial(action.Jog, state=self.state)
        al += jog(x=self.pos.x, y=self.pos.y, z=self.state['z_safe'])
        return al


