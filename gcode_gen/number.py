import numpy as np
from numpy.linalg import norm, det
import itertools
import operator

EPSILON = 1.0e-6
mmPerInch = 25.4

def num2str(arg):
    return "{:.5f}".format(arg)

def floatEq(floatA, floatB, epsilon=EPSILON):
    return abs(floatA - floatB) > EPSILON

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


def monotone_increasing(lst):
    pairs = zip(lst, lst[1:])
    return all(itertools.starmap(operator.le, pairs))

def monotone_decreasing(lst):
    pairs = zip(lst, lst[1:])
    return all(itertools.starmap(operator.ge, pairs))

def monotone(lst):
    return monotone_increasing(lst) or monotone_decreasing(lst)

def isClockwiseVertexList(vertices):
    oMat = np.concatenate((np.ones((3, 1)), vertices[0:3]), axis=1)
    return det(oMat) < 0

def calcStepsWithMaxSpacing(start, stop, maxSpacing):
    # note: safeCeil(abs(stop-start) / maxSpacing) gives the number of intervals,
    # but the number of steps is +1.
    # Why? Think of fenceposts.
    numSteps = safeCeil(abs(stop-start) / maxSpacing) + 1
    stepList = np.linspace(start, stop, numSteps)
    return stepList

calcZSteps = calcStepsWithMaxSpacing

def calcEffectiveToolDiameter(toolCutDiameter, overlap):
    return toolCutDiameter * (1 - overlap)

def calcFillSteps(start, stop, toolCutDiameter, overlap):
    maxSpacing = calcEffectiveToolDiameter(toolCutDiameter, overlap)
    return calcStepsWithMaxSpacing(start, stop, maxSpacing)

def calcRSteps(desiredDiameter, toolCutDiameter, overlap):
    maxSpacing = calcEffectiveToolDiameter(toolCutDiameter, overlap)
    return calcStepsWithMaxSpacing(maxSpacing , desiredDiameter / 2 - maxSpacing / 2, maxSpacing)


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


def findBotLeftVertexIdx(vertices):
    botLeftIdx = None
    for idx, (x, y) in enumerate(vertices):
        if botLeftIdx is None:
            botLeftIdx = idx
        else:
            # print("botLeft: {}, x,y: {}, {}".format(botLeft, x, y))
            if y < vertices[botLeftIdx][1]:
                botLeftIdx = idx
            elif y == vertices[botLeftIdx][1]:
                if x < vertices[botLeftIdx][0]:
                    botLeftIdx = idx
        # print(x, y, idx, botLeftIdx, vertices[botLeftIdx], y < vertices[botLeftIdx][1], y == vertices[botLeftIdx][1])
    return botLeftIdx


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

