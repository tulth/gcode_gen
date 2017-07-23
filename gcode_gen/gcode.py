'''
Library for gcode commands objects that render to strings.
'''
from .number import num2str
from .point import XYZ


class GcodePoint(XYZ):
    def __str__(self):
        ret_list = []
        for label, val in zip(('X', 'Y', 'Z'), self.xyz):
            if val is not None:
                ret_list.append('{}{}'.format(label, num2str(val)))
        return ' '.join(ret_list)


class BaseGcode(object):
    def __init__(self, cmd, x=None, y=None, z=None):
        super().__init__()
        self.cmd = cmd
        self.point = GcodePoint(x, y, z)

    def __str__(self):
        point_str = str(self.point)
        if point_str != '':
            point_str = ' ' + point_str
        return '{}{}'.format(self.cmd, point_str)


class Home(BaseGcode):
    '''homing cycle'''
    def __init__(self):
        super().__init__('$H')


class Comment(BaseGcode):
    '''comment'''
    def __str__(self):
        return '({})'.format(self.cmd)


class UnitsInches(BaseGcode):
    '''Set system units to inches'''
    def __init__(self):
        super().__init__('G20')


class UnitsMillimeters(BaseGcode):
    '''Set system units to millimeters'''
    def __init__(self):
        super().__init__('G21')


class MotionAbsolute(BaseGcode):
    '''Set system to use absolute motion'''
    def __init__(self):
        super().__init__('G90')


class MotionRelative(BaseGcode):
    '''Set system to use relative motion'''
    def __init__(self):
        raise Exception('Not supported!!')
        # super().__init__('G91')


class SetSpindleSpeed(BaseGcode):
    '''Set spindle rotation speed'''
    def __init__(self, spindle_speed):
        super().__init__('S {}'.format(spindle_speed))


class SetFeedRate(BaseGcode):
    '''set feed rate.  CAUTION: feed rate is system units per minute'''
    def __init__(self, feedRate):
        self.feedRate = feedRate
        super().__init__('F {}'.format(feedRate))


class ActivateSpindleCW(BaseGcode):
    '''Activate spindle (clockwise)'''
    def __init__(self, ):
        super().__init__('M3')


class StopSpindle(BaseGcode):
    '''Stop spindle'''
    def __init__(self, ):
        super().__init__('M5')


class G0(BaseGcode):
    '''linear NONcut motion'''
    def __init__(self, x=None, y=None, z=None):
        super().__init__('G0', x, y, z)


class G1(BaseGcode):
    '''linear CUT motion'''
    def __init__(self, x=None, y=None, z=None):
        super().__init__('G1', x, y, z)


class BaseArcGcode(BaseGcode):
    def __init__(self, cmd, x=None, y=None, z=None, r=None):
        assert r is not None
        # need at least one rectangular coordinate
        assert not all(rect_coord is None for rect_coord in (x, y, z))
        self.radius = r
        super().__init__(cmd, x, y, z)

    def __str__(self):
        return "{} R{}".format(super().__str__(), num2str(self.radius))


class G2(BaseArcGcode):
    '''clockwise arc CUT motion'''
    def __init__(self, x=None, y=None, z=None, r=None):
        super().__init__('G2', x, y, z, r)


class G3(BaseArcGcode):
    '''clockwise arc CUT motion'''
    def __init__(self, x=None, y=None, z=None, r=None):
        super().__init__('G3', x, y, z, r)

