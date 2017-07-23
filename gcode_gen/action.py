'''Library for 'Actions' representing cnc position or state updates and lists of actions'''
from collections import UserList
from . import gcode as gc
from . import point as pt


class Action(object):
    '''Represents a single CNC position or state update'''
    def __init__(self, state=None):
        super().__init__()
        self.state = state

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
        self.pos = pt.Point(*xyz)

    def get_gcode(self):
        raise NotImplementedError('define gcode generation in base class')

    def get_points(self):
        raise NotImplementedError('define gcode generation in base class')

    def __iter__(self):
        yield self


class GcodeMotionXYZ(Action):
    def __init__(self, gcode_class, x=None, y=None, z=None, state=None):
        super().__init__(state=state)
        old_pos = self.pos
        self.pos_mv(x, y, z)
        self.changes = pt.changes(old_pos, self.pos)
        self.gcode_class = gcode_class

    def get_gcode(self):
        if self.changes:
            return (self.gcode_class(**self.changes), )
        else:
            return ()


class Jog(GcodeMotionXYZ):
    def __init__(self, x=None, y=None, z=None, state=None):
        super().__init__(gcode_class=gc.G0,
                         x=x, y=y, z=z,
                         state=state)


class Cut(GcodeMotionXYZ):
    def __init__(self, x=None, y=None, z=None, state=None):
        super().__init__(gcode_class=gc.G1,
                         x=x, y=y, z=z,
                         state=state)


class SetDrillFeedRate(Action):
    def __init__(self, state=None):
        super().__init__(state=state)
        fr = self.state['drilling_feed_rate']
        if self.state['feed_rate'] != fr:
            self.state['feed_rate'] = fr
            self.gc = (gc.SetFeedRate(fr), )
        else:
            self.gc = ()

    def get_gcode(self):
        return self.gc


class SetMillFeedRate(Action):
    def __init__(self, state=None):
        super().__init__(state=state)
        fr = self.state['milling_feed_rate']
        if self.state['feed_rate'] != fr:
            self.state['feed_rate'] = fr
            self.gc = (gc.SetFeedRate(fr), )
        else:
            self.gc = ()

    def get_gcode(self):
        return self.gc


class ActionList(UserList):
    def append(self, arg):
        self.check_type(arg)
        super().append(arg)

    def extend(self, arg):
        for elem in arg:
            self.check_type(elem)
        super().extend(arg)

    def check_type(self, other):
        if not isinstance(other, Action):
            raise TypeError('expected Action type')

    def get_gcode(self):
        result = []
        for elem in self:
            result.extend(elem.get_gcode())
        return result


