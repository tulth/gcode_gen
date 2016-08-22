#!/bin/env python
"""
lib for gcode gen (and openscad gen).
All numbers represent millimeters.

"""
from __future__ import print_function
import sys
import logging
import argparse
import collections
import numpy as np
from numpy.linalg import norm

import gen_scad

log = logging.getLogger()
# log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stdout)
log.addHandler(logHandler)

EPSILON = 1.0e-6
mmPerInch = 25.4

def num2str(arg):
    return "{:.5f}".format(arg)

class Action(object):
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

    def genScad(self, prevPoint):
        return [((tuple(prevPoint), tuple(self.point), ))]

    def compress(self, prevPoint):
        self.point.compress(prevPoint)

    def isPrunable(self):
        return False

class cmd_home(Action):
    """homing cycle"""
    def __init__(self):
        super().__init__("$H")


class cmd_comment(Action):
    """comment"""

    def __str__(self):
        return "comment:{} point:{}".format(self.cmd, self.point)

    def genGcode(self):
        return "({})".format(self.cmd)


class cmd_unitsInches(Action):
    """Set system units to inches"""
    def __init__(self):
        super().__init__("G20")


class cmd_unitsMillimeters(Action):
    """Set system units to millimeters"""
    def __init__(self):
        super().__init__("G21")


class cmd_motionAbsolute(Action):
    """Set system to use absolute motion"""
    def __init__(self):
        super().__init__("G90")


class cmd_motionRelative(Action):
    """Set system to use relative motion"""
    def __init__(self):
        raise Exception("Not supported!!")
        # super().__init__("G91")

class cmd_setSpindleSpeed(Action):
    """Set spindle rotation speed"""
    def __init__(self, spindleSpeed):
        super().__init__("S {}".format(spindleSpeed))

class cmd_setFeedRate(Action):
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

class cmd_motionAbsolute(Action):
    """Set system to use absolute motion"""
    def __init__(self):
        super().__init__("G90")

class cmd_activateSpindleCW(Action):
    """Activate spindle (clockwise)"""
    def __init__(self, ):
        super().__init__("M3")

class cmd_stopSpindle(Action):
    """Stop spindle"""
    def __init__(self, ):
        super().__init__("M5")


class cmd_g0(Action):
    """linear NONcut motion"""
    def __init__(self, x=None, y=None, z=None):
        super().__init__("G0", x, y, z)

    def isPrunable(self):
        for val in self.point:
            if val is not None:
                return False
        return True

class cmd_g1(Action):
    """linear CUT motion"""
    def __init__(self, x=None, y=None, z=None):
        super().__init__("G1", x, y, z)

    def isPrunable(self):
        for val in self.point:
            if val is not None:
                return False
        return True

class cmd_g2(Action):
    """clockwise arc CUT motion"""
    def __init__(self, x=None, y=None, z=None, r=None):
        assert r is not None
        self.radius = r
        super().__init__("G2", x, y, z, )

    def genGcode(self):
        pointStr = str(self.point)
        if pointStr != "":
            pointStr = " " + pointStr
        return "{}{} R{}".format(self.cmd, pointStr, num2str(self.radius))

    def isPrunable(self):
        for val in self.point:
            if val is not None:
                return False
        return True

    def genScad(self, prevPoint):
        # print("prevPoint: {}".format(prevPoint))
        # print("self.point: {}".format(self.point))
        segs = arc2segments(prevPoint[0:2], self.point[0:2], self.radius, clockwise=True)
        prevSeg = prevPoint
        results = []
        for seg in segs:
            segAsPoint = point(*seg)
            segAsPoint.expand(prevPoint)
            results.append([tuple(prevSeg), tuple(segAsPoint)])
            prevSeg = segAsPoint
        return results
        #return ((tuple(prevPoint), tuple(self.point), ))

class cmd_arcInXYPlane(Action):
    """Select the XY plane (for arcs)"""
    def __init__(self, ):
        super().__init__("G17", )


class Assembly(object):
    def __init__(self, *args, **kwargs):
        super().__init__()
        baseKwargs = {"name": None, "cncCfg": None }
        self.args = args
        self.kwargs = kwargs
        for argName in baseKwargs:
            if argName in self.kwargs:
                baseKwargs[argName] = self.kwargs[argName]
                del self.kwargs[argName]
        self._init(**baseKwargs)

    def _init(self, name=None, cncCfg=None, ):
        if name is None:
            name = self.defaultName()
        self.name = name
        self.cncCfg = cncCfg
        self.children = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if exc[0] is not None:
            return False
        self.elab()
        return False

    def defaultName(self):
        return self.__class__.__name__

    def checkType(self, other):
        assert isinstance(other, Assembly) or isinstance(other, Action)

    def __iadd__(self, other):
        self.checkType(other)
        # self.children.append(other)
        # if isinstance(other, Assembly):
        #     other.cncCfg = self.cncCfg
        #     other.elab()
        if isinstance(other, Assembly):
            with other:
                other.cncCfg = self.cncCfg
        self.children.append(other)
        return self

    def __str__(self):
        return self.treeStr()

    @property
    def label(self):
        return "Assm:{}".format(self.name)

    def treeStr(self, indent=0):
        strList = ["{}{}".format(indent * " ", self.label)]
        for child in self.children:
            if isinstance(child, Assembly):
                strList.append(child.treeStr(indent + 2))
            else:
                strList.append("{}{}".format((indent + 2) * " ", child))
        return "\n".join(strList)

    def genGcode(self):
        flatAsm = self.getFlattened()
        return flatAsm.genGcode()

    def getScad(self):
        flatAsm = self.getFlattened()
        return flatAsm.genGcode()

    def getFlattened(self):
        flatAsm = FlattenedAssembly()
        flatAsm.append(FlattenedAssemblyEntry("({})".format(self.label)))
        for child in self.children:
            if isinstance(child, Assembly):
                flatAsm.extend(child.getFlattened())
            else:
                flatAsm.append(child)
        return flatAsm

    def elab(self):
        self._elab(*self.args, **self.kwargs)

    def expand(self):
        for child in self.children:
            if isinstance(child, Assembly):
                child.expand()
            else:
                if isinstance(child, cmd_setFeedRate):
                    child.expand(self.cncCfg["lastPosition"], self.cncCfg["lastFeedRate"])
                    self.cncCfg["lastFeedRate"] = child.feedRate
                else:
                    child.expand(self.cncCfg["lastPosition"])
                self.cncCfg["lastPosition"] = child.point

    def genScad(self):
        pointPairList = []
        for child in self.children:
            if isinstance(child, Assembly):
                pointPairList.extend(child.genScad())
            else:
                pointPairList.extend(child.genScad(self.cncCfg["lastPosition"]))
                self.cncCfg["lastPosition"] = child.point
        return pointPairList

    def compress(self):
        childIdxsToPrune = []
        for childIdx, child in enumerate(self.children):
            if isinstance(child, Assembly):
                child.compress()
            else:
                if isinstance(child, cmd_setFeedRate):
                    child.compress(self.cncCfg["lastPosition"], self.cncCfg["lastFeedRate"])
                    if child.feedRate is not None:
                        self.cncCfg["lastFeedRate"] = child.feedRate
                else:
                    child.compress(self.cncCfg["lastPosition"])
                for idx, val in enumerate(child.point):
                    if val is not None:
                        self.cncCfg["lastPosition"][idx] = val
                if child.isPrunable():
                    childIdxsToPrune.append(childIdx)
        # prune
        self.children = [val for idx, val in enumerate(self.children) if idx not in childIdxsToPrune]

    def _elab(self):
        """Define in subclass, it will get all __init__ args except name, cncCfg"""
        raise NotImpementedError()

class FlattenedAssemblyEntry(Action):
    pass

class FlattenedAssembly(list):

    def genGcode(self):
        strList = []
        for entry in self:
            strList.append(entry.genGcode())
        return "\n".join(strList)

class asm_header(Assembly):

    def _elab(self):
        self += cmd_home()
        self += cmd_unitsMillimeters()
        self += cmd_motionAbsolute()
        self += cmd_setSpindleSpeed(self.cncCfg["spindleSpeed"])
        self += cmd_activateSpindleCW()
        self += cmd_g0(z=self.cncCfg["zSafe"])
        self += cmd_setFeedRate(self.cncCfg["defaultMillingFeedRate"])
        self += cmd_arcInXYPlane()


class asm_footer(Assembly):

    def _elab(self):
        self += cmd_g0(z=self.cncCfg["zSafe"])
        self += cmd_stopSpindle()
        self += cmd_home()


class asm_file(Assembly):
    def __init__(self, name=None, cncCfg=None, comments=()):
        super().__init__(name=name, cncCfg=cncCfg, )
        for comment in comments:
            self += cmd_comment(comment)
        self += asm_header()

    def elab(self):
        self += asm_footer()
        self.expand()
        self.compress()

    def expand(self):
        self.cncCfg["lastPosition"] = point(0, 0, 70)  # homed at x/y=0, but z is indeterminate, estimating 70
        self.cncCfg["lastFeedRate"] = -1
        super().expand()

    def genScad(self):
        self.expand()
        self.compress()
        self.expand()
        # print(self)
        # sys.exit()
        self.cncCfg["lastPosition"] = point(0, 0, 70)  # homed at x/y=0, but z is indeterminate, estimating 70
        self.cncCfg["lastFeedRate"] = -1
        pointPairList = super().genScad()
        result = gen_scad.genScad(pointPairList)
        self.compress()
        return result

    def compress(self):
        self.cncCfg["lastPosition"] = point(0, 0, 70)  # homed at x/y=0, but z is indeterminate, estimating 70
        self.cncCfg["lastFeedRate"] = -1
        super().compress()


class asm_drillHole(Assembly):

    def _elab(self,
              xCenter, yCenter,
              zTop, zBottom,
              name="drillHole",
              plungeRate=None, zMargin=None, ):
        if plungeRate is None:
            plungeRate = self.cncCfg["defaultDrillingFeedRate"]
        if zMargin is None:
            zMargin = self.cncCfg["zMargin"]
        self += cmd_g0(z=self.cncCfg["zSafe"])
        self += cmd_g0(xCenter, yCenter)
        self += cmd_g0(z=zMargin + zTop)
        self += cmd_setFeedRate(plungeRate)
        self += cmd_g1(z=zBottom)
        self += cmd_g1(z=zTop)
        self += cmd_g0(z=zMargin + zTop)
        self += cmd_g0(z=self.cncCfg["zSafe"])

def floatEq(floatA, floatB, epsilon=EPSILON):
    return abs(floatA - floatB) > EPSILON    

def calcZSteps(zTop, zBottom, depthPerPass):
    zCutList = [zTop]
    for cutNum in range(int((zTop - zBottom) / depthPerPass)):
        zCutList += [zTop - ((cutNum + 1) * depthPerPass)]
    if floatEq(zCutList[-1], zBottom):
        zCutList += [zBottom]
    return zCutList


def calcRSteps(desiredDiameter, toolDiameter, overlap):
    cutRList = []
    wtd = toolDiameter * (1 - overlap)
    startRadius = wtd / 2  # because the first Z movedown drills out the center
    endRadius = desiredDiameter / 2 - wtd / 2  # because we do a final exact ring pass
    for cutNum in range(int((endRadius - startRadius) / wtd) + 1):
        cutR = (cutNum * wtd + 2 * startRadius)
        if cutR >= desiredDiameter / 2 - toolDiameter / 2:
            break
        cutRList += [cutR]
    cutRList += [desiredDiameter / 2 - toolDiameter / 2]
    return cutRList



class asm_circle(Assembly):
    """clockwise circle, XY plane only!"""
    def _elab(self,
              xCenter, yCenter, r):
        cardinalPoints = ((xCenter, yCenter + r),
                          (xCenter + r, yCenter),
                          (xCenter, yCenter - r),
                          (xCenter - r, yCenter))
        self += cmd_setFeedRate(self.cncCfg["defaultMillingFeedRate"])
        self += cmd_g1(*(cardinalPoints[-1]))
        for p in cardinalPoints:
            x, y = p
            self += cmd_g2(x, y, r=r)


class asm_filledCircleCut(Assembly):
    def _elab(self,
              xCenter, yCenter, zCut, diameter,
              overlap=None):
        if overlap is None:
            overlap = self.cncCfg["defaultMillingOverlap"]
        cutRList = calcRSteps(diameter, self.cncCfg["tool"].cutDiameter, overlap)
        self += cmd_setFeedRate(self.cncCfg["defaultDrillingFeedRate"])
        self += cmd_g1(z=zCut)
        for cutCircleR in cutRList:
            self += asm_circle(xCenter, yCenter, cutCircleR)
        self += cmd_setFeedRate(self.cncCfg["defaultMillingFeedRate"])
        self += cmd_g1(xCenter, yCenter)

class asm_cylinderCut(Assembly):
    def _elab(self,
              xCenter, yCenter, zTop, zBottom, diameter,
              overlap=None):
        if overlap is None:
            overlap = self.cncCfg["defaultMillingOverlap"]
        cutZList = calcZSteps(zTop, zBottom, self.cncCfg["defaultDepthPerMillingPass"])
        self += cmd_g0(xCenter, yCenter)
        self += cmd_g0(z=self.cncCfg["zMargin"] + zTop)
        for cutZ in cutZList:
            self += asm_filledCircleCut(xCenter, yCenter, cutZ, diameter,
                                        overlap=overlap)

class point(np.ndarray):
    def __new__(cls, x=None, y=None, z=None):
        floatOrNoneCoord = []
        for val in (x, y, z):
            if val is None:
                floatOrNoneCoord.append(None)
            else:
                floatOrNoneCoord.append(float(val))
        obj = np.asarray(floatOrNoneCoord, dtype=object).view(cls)
        return obj

    def __array_finalize__(self, obj):
        self.info = getattr(obj, 'info', None)

    def __str__(self):
        retList = []
        for label, val in zip(("X", "Y", "Z"), self):
            if val is not None:
                retList.append("{}{}".format(label, num2str(val)))
        return " ".join(retList)

    def expand(self, prevPoint):
        for idx, val in enumerate(self):
            if val is None:
                self[idx] = prevPoint[idx]
        
    def compress(self, prevPoint):
        for idx, val in enumerate(self):
            if prevPoint[idx] is None:
                pass
            else:
                if abs(self[idx] - prevPoint[idx]) < EPSILON:
                    self[idx] = None


class Tool(object):
    def __init__(self,
                 cutDiameter,
                 shankDiameter=3.175, ):
        self.cutDiameter = cutDiameter
        self.shankDiameter = shankDiameter

class CncMachineConfig(dict):
    def __init__(self,
                 tool,
                 zSafe,
                 spindleSpeed=10000,
                 defaultDepthPerMillingPass=0.4,
                 defaultMillingFeedRate=150,
                 defaultDrillingFeedRate=20,
                 defaultMillingOverlap=0.15,
                 zMargin=2):
        assert isinstance(tool, Tool)
        super().__init__()
        self["tool"] = tool
        self["zSafe"] = zSafe
        self["spindleSpeed"] = spindleSpeed
        self["defaultDepthPerMillingPass"] = defaultDepthPerMillingPass
        self["defaultMillingFeedRate"] = defaultMillingFeedRate
        self["defaultDrillingFeedRate"] = defaultDrillingFeedRate
        self["defaultMillingOverlap"] = defaultMillingOverlap
        self["zMargin"] = zMargin
        self["lastPosition"] = point(0, 0, 70)  # homed at x/y=0, but z is indeterminate, estimating 70
        self["lastFeedRate"] = -1


def demo(argv):
    cfg = parseArgs(argv)
    arc2segmentsDemo()
    toolDia = (1 / 8) * mmPerInch
    comments = []
    comments.append('Use {}" ball nose'.format(toolDia / mmPerInch))
    comments.append("Home first!  Zero X and Y at home!")
    comments.append("Zero Z manually using a sheet of paper!")

    tool=Tool(cutDiameter=toolDia)
    cncCfg = CncMachineConfig(tool,
                              zSafe=20,
                              )
    #
    holeDepth = 0.35 * mmPerInch
    botRight = (-20, -180)
    centers = []
    offsets = [offsetInches * mmPerInch for offsetInches in (0.5, 1.5)]
    for offset in offsets:
        centers.append((botRight[0] + toolDia / 2, botRight[1] + offset))
    for offset in offsets:
        centers.append((botRight[0] - offset, botRight[1] - toolDia / 2))
    centers = [[0, 0]]
    asmFile = asm_file(name="Demo", cncCfg=cncCfg, comments=comments)
    with asmFile as asm:
        for center in centers:
            asm += asm_cylinderCut(center[0], center[1],
                                   zTop=0, zBottom=-0.4, diameter=10)
            #asm += cmd_g0(z=cncCfg["zSafe"])

    log.info("*****\n{}\n".format(asmFile))
    log.info("*****\n{}\n".format(asmFile.genGcode()))
    asmFile.expand()
    log.info("*****\n{}\n".format(asmFile.genGcode()))
    asmFile.compress()
    log.info("*****\n{}\n".format(asmFile.genGcode()))
    log.info("*****\n{}\n".format(asmFile))
    scadFileName = "demo.scad"
    with open(scadFileName, 'w') as ofp:
        ofp.write(asmFile.genScad())
    log.info("wrote {}".format(scadFileName))
    gcodeFileName = "demo.gcode"
    with open(gcodeFileName, 'w') as ofp:
        ofp.write(asmFile.genGcode())
    log.info("wrote {}".format(gcodeFileName))
    return 0

def parseArgs(argv):
    description = __doc__
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    # if len(argv) == 1:
    #     argv.append('-h')

    parser.add_argument('-d', '--debug',
                        help='Turn on debug printing.',
                        action='store_true',)
    cfg = parser.parse_args()
    return cfg

def cart2pol(pt):
    x, y = pt
    r = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    phi = phiNorm(phi)
    return np.asarray((r, phi), dtype=float)

def pol2cart(polPt):
    r, phi = polPt
    log.debug("pol2cart r, phi: {}, {}".format(r, phi * 180 / 2 / np.pi))
    x = r * np.cos(phi)
    y = r * np.sin(phi)
    log.debug("pol2cart x, y: {}, {}".format(x, y))
    return np.asarray((x, y), dtype=float)


def rotateVec90DegreesCounterClockwise(vec):
    result = vec.copy()
    result[0] = -vec[1]
    result[1] = vec[0]
    return result

def absDeltaPhi(u, v):
    """Given two vectors, return the ABS angle between them"""
    c = np.dot(u, v) / (norm(u) * norm(v)) # -> cosine of the angle
    phi = np.arccos(np.clip(c, -1, 1))
    return phi

def determinant(u, v):
    return u[0] * v[1] - u[1] * v[0]

def deltaPhi(u, v):
    """Given two vectors, return the angle between them, where positive angles correspond to clockwise motion"""
    phi = absDeltaPhi(u, v)
    log.debug("abs phi: {}".format(phi))
    if determinant(u, v) >= 0:
        phi += 2 * np.pi
    return phi
    # c = np.dot(u, v) / (norm(u) * norm(v)) # -> cosine of the angle
    # phi = np.arccos(np.clip(c, -1, 1))
    # return phi
              
def arc2segmentsFindCenter(p0, p1, r, clockwise=True):
    if clockwise:
        direction = -1
    else:
        direction = 1
    distanceBetweenp0p1, unused = cart2pol(p1 - p0)
    midpointBetweenp0p1 = (p1 + p0) / 2
    unitVecFromp0Top1 = (p1 - p0) / distanceBetweenp0p1
    unitVecFromp0Top1Rotated90DegreesCounterClockwise = rotateVec90DegreesCounterClockwise(unitVecFromp0Top1)
    unitVecFromp0Top1Rotated90DegreesCounterClockwise[0] = -unitVecFromp0Top1[1]
    unitVecFromp0Top1Rotated90DegreesCounterClockwise[1] = unitVecFromp0Top1[0]
    distanceFromCenterToMidpoint = np.sqrt(r**2 - (distanceBetweenp0p1/2)**2)
    center = (midpointBetweenp0p1 +
              direction * distanceFromCenterToMidpoint * unitVecFromp0Top1Rotated90DegreesCounterClockwise)
    return center

def safeCeil(arg, epsilon=EPSILON):
    """Ceiling of arg, but if arg is within epsilon of an integer just return that int.
    Example: safeCeil(3.999999) == 4
    Example: safeCeil(4.00000001) == 4
    Example: safeCeil(4.1) == 5"""
    if abs(arg - round(arg)) <= epsilon:
        return int(round(arg))
    else:
        return int(np.ceil(arg))
    
assert safeCeil(3.999999) == 4
assert safeCeil(4.00000001) == 4
assert safeCeil(4.1) == 5

def phiNorm(phi):
    while phi < 0:
        phi += 2 * np.pi
    while phi >= 2 * np.pi:
        phi -= 2 * np.pi
    return phi

def arc2segments(p0, p1, r, segmentPerCircle=16, clockwise=True):
    assert clockwise == True  # ccw case not tested!
    log.debug("p0: {}".format(p0))
    log.debug("p1: {}".format(p1))
    log.debug("r: {}".format(r))
    center = arc2segmentsFindCenter(p0, p1, r)
    # import matplotlib.pyplot as plt
    # plt.figure()
    # plt.plot([p0[0]], [p0[1]], 'gx')
    # plt.plot([center[0]], [center[1]], 'bx')
    # plt.plot([p1[0]], [p1[1]], 'rx')
    # plt.grid()
    # plt.axes().set_aspect('equal')
    # plt.show()
    log.debug("center: {}".format(center))
    p0RelativeToCenter = p0 - center
    p1RelativeToCenter = p1 - center
    log.debug("center, p0RelativeToCenter, p1RelativeToCenter: {}, {}, {}".format(center, p0RelativeToCenter, p1RelativeToCenter))
    unused, phi0 = cart2pol(p0RelativeToCenter)
    dphi = phiNorm(deltaPhi(p0RelativeToCenter, p1RelativeToCenter))
    log.debug("dphi: {}".format(dphi / np.pi * 180))
    circleFract = abs(dphi / 2 / np.pi)
    log.debug("circleFract: {}".format(circleFract))
    numSegmentsFloat = circleFract * segmentPerCircle
    log.debug("numSegmentsFloat: {}".format(numSegmentsFloat))
    numSegments = safeCeil(numSegmentsFloat)
    log.debug("numSegments: {}".format(numSegments))
    phiStep = dphi / numSegments
    results = []
    for segmentNum in range(numSegments):
        phi = phi0 - (segmentNum + 1) * phiStep
        log.debug("phi: {}".format(phi / np.pi * 180))
        # point = r * np.asarray([np.sin(phi), np.cos(phi)], dtype=float) + center
        point = pol2cart((r, phi)) + center
        # [array([ 0.92387953, -0.38268343]), array([ 0.70710678, -0.70710678]), array([ 0.38268343, -0.92387953]), array([  2.33486982e-16,  -1.00000000e+00])]
        results.append(point)
    log.debug(results)
    xPoints = [p0[0]] + [result[0] for result in results]
    yPoints = [p0[1]] + [result[1] for result in results]
    # import matplotlib.pyplot as plt
    # plt.figure()
    # plt.plot([x - center[0] for x in xPoints], [y - center[1] for y in yPoints], 'bo-')
    # plt.hold(True)
    # plt.plot([p0[0] - center[0]], [p0[1] - center[1]], 'rx')
    # plt.grid()
    # plt.axes().set_aspect('equal')
    # plt.figure()
    # plt.plot(xPoints, yPoints, 'bo-')
    # plt.hold(True)
    # plt.plot([p0[0]], [p0[1]], 'rx')
    # plt.grid()
    # plt.axes().set_aspect('equal')
    # #plt.axis([-1,1,-1,1])
    # # log.debug(plt.axis())
    # plt.show()
    return results


def calcZigZagSteps(start, stop, cutDia, overlap):
    stepList = [start]
    workStep = cutDia * (1 - overlap)
    numSteps = safeCeil((stop-start) / workStep)
    stepList = np.linspace(start, stop, numSteps)
    # for cutNum in range(int((stop - start) / workStep)):
    #     stepList += [start + ((cutNum + 1) * workStep)]
    # if floatEq(stepList[-1], stop):
    #     stepList += [stop]
    return stepList

def serpentIter(starts, stops):
    directionStartToStop = True
    for start, stop in zip(starts, stops):
        if directionStartToStop:
            yield start
            yield stop
        else:
            yield stop
            yield start
        directionStartToStop = not(directionStartToStop)

def twiceIter(baseIter):
    for val in baseIter:
        yield val
        yield val

class asm_interpolatedSerpentineCut(Assembly):
    """Back and forth, scanline-like cut pattern.
Starts at bottom left point and moves left to right, then up, then right to left, then up, repeat.
Automatically cuts from yBottom to yBottom + yHeight using a series of horizontal lines.
Linearly interpolates to each line's x-start and x-end based on right and left points.
For example, for a side=1 hexagon, one might specify:
yFractXStartEnds = ((0,    0,    1),   # at start height 0, cut from 0 to 1
                    (0.5, -0.5,  1.5), # at half  height, cut from -0.5 to 1.5
                    (1.0,  0,    1), ) # at end   height, cut from 0 to 1
DOES take into account tool width, but the edges may have uncut bits.
Recommend a final pass around the perimeter, and corner dogbones if needed.
"""
    def _elab(self,
              yBottom,
              yHeight,
              yFractXStartEnds,
              overlap=None):
        if overlap is None:
            overlap = self.cncCfg["defaultMillingOverlap"]
        cutDia = self.cncCfg["tool"].cutDiameter
        ySteps = calcZigZagSteps(yBottom, yBottom + yHeight, cutDia, overlap)
        log.info("ySteps: {}".format(ySteps))
        yParams = [yFractXStartEnd[0] * yHeight for yFractXStartEnd in yFractXStartEnds]
        xStartParams = [yFractXStartEnd[1] for yFractXStartEnd in yFractXStartEnds]
        xStopParams = [yFractXStartEnd[2] for yFractXStartEnd in yFractXStartEnds]
        log.info("yParams: {}".format(yParams))
        log.info("xStartParams: {}".format(xStartParams))
        log.info("xStopParams: {}".format(xStopParams))
        xStartSteps = np.interp(ySteps, yParams, xStartParams)
        xStopSteps = np.interp(ySteps, yParams, xStopParams)
        log.info("xStartSteps: {}".format(xStartSteps))
        log.info("xStopSteps: {}".format(xStopSteps))
        # import matplotlib.pyplot as plt
        # plt.plot(xStartParams, yParams, 'o')
        # plt.plot(xStartSteps, ySteps, '-x')
        # plt.plot(xStopParams, yParams, 'o')
        # plt.plot(xStopSteps, ySteps, '-x')
        # plt.show()
        self += cmd_g0(x=xStartSteps[0], y=yBottom)
        # FIXME ADDME self += cmd_g1(z=cutZ)
        yIter = iter(ySteps)
        for xCoord, yCoord in zip(serpentIter(xStartSteps, xStopSteps), twiceIter(ySteps)):
            log.info("xCoord, yCoord: {}, {}".format(xCoord, yCoord))
            self += cmd_g1(x=xCoord, y=yCoord)
        self += cmd_g0(z=self.cncCfg["zSafe"])


def arc2segmentsDemo():
    offset = np.asarray([0, 0], dtype=float)
    p0 = np.asarray([-21.11125, -167.30000], dtype=float) + offset
    p1 = np.asarray([-18.41250, -164.60125], dtype=float) + offset
    arc2segments(p0, p1, 2.69875)
    p0 = np.asarray([-1, 0], dtype=float) + offset
    p1 = np.asarray([0, 1], dtype=float) + offset
    arc2segments(p0, p1, 1)
    p0 = np.asarray([0, 1], dtype=float) + offset
    p1 = np.asarray([1, 0], dtype=float) + offset
    arc2segments(p0, p1, 1)
    p0 = np.asarray([1, 0], dtype=float) + offset
    p1 = np.asarray([0, -1], dtype=float) + offset
    arc2segments(p0, p1, 1)
    p0 = np.asarray([0, -1], dtype=float) + offset
    p1 = np.asarray([-1, 0], dtype=float) + offset
    arc2segments(p0, p1, 1)
    
if __name__ == '__main__':
    sys.exit(demo(sys.argv))
