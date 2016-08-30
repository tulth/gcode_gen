from . import number
from .number import point
from . import arc2segments

class BaseCmd(object):
    def __init__(self, cmd, x=None, y=None, z=None, r=None):
        super().__init__()
        self.cmd = cmd
        self.point = point(x, y, z)

    def __str__(self):
        return "cmd:{} point:{}".format(self.cmd, self.point)

    def genGcode(self):
        pointStr = str(self.point)
        if pointStr != "":
            pointStr = " " + pointStr
        return "{}{}".format(self.cmd, pointStr)

    def expand(self, prevPoint):
        self.point.expand(prevPoint)

    def genPointPairList(self, prevPoint):
        return [((tuple(prevPoint), tuple(self.point), ))]

    def compress(self, prevPoint):
        self.point.compress(prevPoint)

    def isPrunable(self):
        return False

class Home(BaseCmd):
    """homing cycle"""
    def __init__(self):
        super().__init__("$H")


class Comment(BaseCmd):
    """comment"""

    def __str__(self):
        return "comment:{} point:{}".format(self.cmd, self.point)

    def genGcode(self):
        return "({})".format(self.cmd)


class UnitsInches(BaseCmd):
    """Set system units to inches"""
    def __init__(self):
        super().__init__("G20")


class UnitsMillimeters(BaseCmd):
    """Set system units to millimeters"""
    def __init__(self):
        super().__init__("G21")


class MotionAbsolute(BaseCmd):
    """Set system to use absolute motion"""
    def __init__(self):
        super().__init__("G90")


class MotionRelative(BaseCmd):
    """Set system to use relative motion"""
    def __init__(self):
        raise Exception("Not supported!!")
        # super().__init__("G91")

class SetSpindleSpeed(BaseCmd):
    """Set spindle rotation speed"""
    def __init__(self, spindleSpeed):
        super().__init__("S {}".format(spindleSpeed))

class SetFeedRate(BaseCmd):
    """set feed rate.  CAUTION: feed rate is system units per minute"""
    def __init__(self, feedRate):
        self.feedRate = feedRate
        super().__init__("F {}".format(feedRate))

    def expand(self, prevPoint, prevFeedrate):
        super().expand(prevPoint)
        if self.feedRate is None:
            self.feedRate = prevFeedrate

    def compress(self, prevPoint, prevFeedrate):
        super().compress(prevPoint)
        if prevFeedrate == self.feedRate:
            self.feedRate = None

    def isPrunable(self):
        return self.feedRate is None

class MotionAbsolute(BaseCmd):
    """Set system to use absolute motion"""
    def __init__(self):
        super().__init__("G90")

class ActivateSpindleCW(BaseCmd):
    """Activate spindle (clockwise)"""
    def __init__(self, ):
        super().__init__("M3")

class StopSpindle(BaseCmd):
    """Stop spindle"""
    def __init__(self, ):
        super().__init__("M5")


class G0(BaseCmd):
    """linear NONcut motion"""
    def __init__(self, x=None, y=None, z=None):
        super().__init__("G0", x, y, z)

    def isPrunable(self):
        for val in self.point:
            if val is not None:
                return False
        return True

class G1(BaseCmd):
    """linear CUT motion"""
    def __init__(self, x=None, y=None, z=None):
        super().__init__("G1", x, y, z)

    def isPrunable(self):
        for val in self.point:
            if val is not None:
                return False
        return True

class G2(BaseCmd):
    """clockwise arc CUT motion"""
    def __init__(self, x=None, y=None, z=None, r=None):
        assert r is not None
        self.radius = r
        super().__init__("G2", x, y, z, )

    def genGcode(self):
        pointStr = str(self.point)
        if pointStr != "":
            pointStr = " " + pointStr
        return "{}{} R{}".format(self.cmd, pointStr, number.num2str(self.radius))

    def isPrunable(self):
        for val in self.point:
            if val is not None:
                return False
        return True

    def genPointPairList(self, prevPoint):
        segs = arc2segments.arc2segments(prevPoint[0:2], self.point[0:2], self.radius, clockwise=True)
        prevSeg = prevPoint
        results = []
        for seg in segs:
            segAsPoint = point(*seg)
            segAsPoint.expand(prevPoint)
            results.append([tuple(prevSeg), tuple(segAsPoint)])
            prevSeg = segAsPoint
        return results

class ArcInXYPlane(BaseCmd):
    """Select the XY plane (for arcs)"""
    def __init__(self, ):
        super().__init__("G17", )

