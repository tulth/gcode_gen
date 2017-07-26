'''Library for 'Actions' representing cnc position or state updates and lists of actions'''
from collections import UserList
from . import number
from . import gcode as gc
from . import point as pt


class Action(object):
    '''Represents a single CNC position or state update
    CAUTION: Only update state during __init__
    CAUTION: Do not update state during get_gcode or get_point!
    '''
    def __init__(self, state=None):
        super().__init__()
        self.state = state
        # default point, override in subclass
        self.point = self.state['position']
        self.skip = False

    def get_gcode(self):
        raise NotImplementedError('define gcode generation in base class')

    def get_point(self):
        return (self.point, )

    def __iter__(self):
        yield self

    def __str__(self):
        return "{} {}".format(self.__class__.__name__, self.point)


class Motion(Action):
    '''x, y, and z are new ABSOLUTE points when not None'''
    def __init__(self, x=None, y=None, z=None, state=None):
        super().__init__(state=state)
        last_point = self.point
        self.point = pt.Point(x, y, z)
        state['position'] = self.point
        self.changes = pt.changes(last_point, self.point)
        if not self.changes:
            self.skip = True


class Jog(Motion):
    def get_gcode(self):
        return (gc.G0(**self.changes), )


class Cut(Motion):
    def get_gcode(self):
        return (gc.G1(**self.changes), )


class StateChange(Action):
    def get_gcode(self):
        return self.gc_tuple

    def get_point(self):
        return ()


class GcodeWithoutArg(StateChange):
    GC = None  # Define in subclass

    def __init__(self, state=None):
        super().__init__(state=state)
        if not isinstance(self.GC(), gc.BaseGcode):
            raise NotImplementedError('must have GC gcode command class variable defined')
        self.gc_tuple = (self.GC(), )


class Home(GcodeWithoutArg):
    GC = gc.Home


class Comment(GcodeWithoutArg):
    GC = gc.Comment


class UnitsInches(GcodeWithoutArg):
    GC = gc.UnitsInches


class UnitsMillimeters(GcodeWithoutArg):
    GC = gc.UnitsMillimeters


class MotionAbsolute(GcodeWithoutArg):
    GC = gc.MotionAbsolute


class MotionRelative(GcodeWithoutArg):
    GC = gc.MotionRelative


class ActivateSpindleCW(GcodeWithoutArg):
    GC = gc.ActivateSpindleCW


class StopSpindle(GcodeWithoutArg):
    GC = gc.StopSpindle


class SetFeedRate(StateChange):
    def __init__(self, feed_rate, state=None):
        super().__init__(state=state)
        self.feed_rate = feed_rate
        if self.state['feed_rate'] is None:
            self.skip = False
        elif number.isclose(self.state['feed_rate'], self.feed_rate):
            self.skip = True
        if self.skip:
            self.gc_tuple = ()
        else:
            self.state['feed_rate'] = self.feed_rate
            self.gc_tuple = (gc.SetFeedRate(self.feed_rate), )

    def __str__(self):
        return "{} {} {}".format(self.__class__.__name__, self.point, number.num2str(self.feed_rate))


class SetDrillFeedRate(SetFeedRate):
    def __init__(self, state=None):
        super().__init__(feed_rate=state['drilling_feed_rate'],
                         state=state)


class SetMillFeedRate(SetFeedRate):
    def __init__(self, state=None):
        super().__init__(feed_rate=state['milling_feed_rate'],
                         state=state)


class SetSpindleSpeed(StateChange):
    def __init__(self, spindle_speed, state=None):
        super().__init__(state=state)
        self.spindle_speed = spindle_speed
        if self.state['spindle_speed'] != self.spindle_speed:
            self.state['spindle_speed'] = self.spindle_speed
            self.gc_tuple = (gc.SetSpindleSpeed(self.spindle_speed), )
        else:
            self.skip = True
            self.gc_tuple = ()

    def __str__(self):
        return "{} {} {}".format(self.__class__.__name__, self.point, self.spindle_speed)


class ActionList(UserList):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.drop_skip = True

    def append(self, arg):
        self.check_type(arg)
        if not arg.skip and self.drop_skip:
            super().append(arg)

    def extend(self, arg):
        if arg == []:
            return
        if arg == ():
            return
        for elem in arg:
            self.append(elem)

    def check_type(self, other):
        if not isinstance(other, Action):
            raise TypeError('expected Action type, got {}'.format(type(other)))

    def get_gcode(self):
        result = []
        for elem in self:
            result.extend(elem.get_gcode())
        return result

    def get_points(self):
        pl = pt.PointList()
        for elem in self:
            new_pt_tuple = elem.get_point()
            if len(new_pt_tuple) == 1:
                pl.append(new_pt_tuple[0])  # compress points that are identical
            elif len(new_pt_tuple) > 1:
                raise TypeError('get_point must return either an empty tuple or a tuple containing a single point')
        return pl

    def __str__(self):
        return '\n'.join(map(str, self))
