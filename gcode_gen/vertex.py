import numpy as np
from numpy.linalg import norm
import itertools
import operator
from . import number

def edgeEndPointCrossproductsIter(vertices):
    for edge in verticesToEdgesIter(vertices):
        yield np.cross(edge[0], edge[1])
        
def isConvex(vertices):
    cpSign = None
    for cp in edgeEndPointCrossproductsIter(vertices):
        cpCmp = (cp > 0) - (cp < 0)
        if cpCmp == 0:
            pass
        elif cpSign is None:
            signPos = cpCmp
        elif cpSign != cpCmp:
            return False
    return True

def isClockwiseVertices(vertices):
    underEdgeAccumTimes2 = 0
    for cp in edgeEndPointCrossproductsIter(vertices):
        underEdgeAccumTimes2 += cp
    return underEdgeAccumTimes2 > 0

def isCounterClockwiseVertices(vertices):
    return not isClockwiseVertices(vertices)

def findBotLeftVertexIdx(vertices):
    botLeftIdx = None
    for idx, (x, y) in enumerate(vertices):
        if botLeftIdx is None:
            botLeftIdx = idx
        else:
            #print(x, y, idx, botLeftIdx, vertices[botLeftIdx], y < vertices[botLeftIdx][1], number.floatEq(y, vertices[botLeftIdx][1]))
            if number.floatEq(y, vertices[botLeftIdx][1]):
                if x < vertices[botLeftIdx][0]:
                    botLeftIdx = idx
            elif y < vertices[botLeftIdx][1]:
                botLeftIdx = idx
        # print(x, y, idx, botLeftIdx, vertices[botLeftIdx], y < vertices[botLeftIdx][1], number.floatEq(y, vertices[botLeftIdx][1]))
    return botLeftIdx

def findTopVertexIdx(vertices):
    topIdx = None
    for idx, vertex in enumerate(vertices):
        if topIdx is None or vertex[1] > vertices[topIdx][1]:
            topIdx = idx
    return topIdx

def verticesToEdgesIter(vertices):
    return number.loopPairsIter(vertices)

def edgesToCornersIter(edges):
    return number.loopPairsIter(edges)

def verticesToCornersIter(vertices):
    return edgesToCornersIter(verticesToEdgesIter(vertices))

def edgeToVectors(edge):
    return (edge[0] - edge[1], edge[2] - edge[1], )

def cornerToVectors(corner):
    vecCCW = corner[0][0] - corner[0][1]
    vecCW = corner[1][1] - corner[1][0]
    return vecCCW, vecCW

def verticesTo2d(vertices):
    assert vertices.shape[-1] in (2, 3)
    return vertices[:, 0:2]
    
def standardizedConvexPolygonVertices(vertices):
    """vertices should be a numpy ndarray vertex array that lies in a plane parallel to XY.
Returns vertex list in counterclockwise order, with the bottom Left vertex in the 0th position"""
    vertices2d = verticesTo2d(vertices)
    assert isConvex(vertices2d)
    isCW = isClockwiseVertices(vertices2d)
    botLeftVertexIdx = findBotLeftVertexIdx(vertices2d)
    if isCW:
        result = np.flipud(vertices)
        botLeftVertexIdx = len(vertices) - 1 - botLeftVertexIdx
    else:
        result = vertices.copy()
    result = np.roll(result, -botLeftVertexIdx, axis=0)
    return result

def toUnitVec(vec):
    return vec / norm(vec)

def calcCornerCorrectionVecForToolCutDiameter(corner, toolCutDiameter, isOutsideCorrection):
    """ASSUMES corner is a from a vertex list that conforms to standardizedConvexPolygonVertices!"""
    vecCCW, vecCW = cornerToVectors(corner)
    diagonal = (vecCCW + vecCW)
    u_vecCW = toUnitVec(vecCW)
    u_vecCCW = toUnitVec(vecCCW)
    toolCutRadius = toolCutDiameter / 2
    correctionScale = toolCutRadius / np.sqrt(1 - (np.dot(u_vecCW, u_vecCCW))**2)
    if isOutsideCorrection:
        correctionScale = -correctionScale
    correctionVec = (u_vecCW + u_vecCCW) * correctionScale
    CWMoveVec = np.asarray((vecCW[1], -vecCW[0]))
    CWMoveVec = toUnitVec(CWMoveVec) * toolCutRadius
    CCWMoveVec = np.asarray((-vecCCW[1], vecCCW[0]))
    CCWMoveVec = toUnitVec(CCWMoveVec) * toolCutRadius
    # import matplotlib.pyplot as plt
    # ax = plt.axes()
    # ax.arrow(0, 0, vecCW[0], vecCW[1], length_includes_head=True, fc='b', ec='b')
    # ax.arrow(0, 0, vecCCW[0], vecCCW[1], length_includes_head=True, fc='r', ec='r')
    # ax.arrow(0, 0, CWMoveVec[0], CWMoveVec[1], length_includes_head=True, fc='c', ec='c')
    # ax.arrow(0, 0, CCWMoveVec[0], CCWMoveVec[1], length_includes_head=True, fc='m', ec='m')
    # ax.arrow(0, 0, correctionVec[0], correctionVec[1], length_includes_head=True, fc='g', ec='g')
    # ax.arrow(CWMoveVec[0], CWMoveVec[1], vecCW[0], vecCW[1], length_includes_head=True, fc='b', ec='b')
    # ax.arrow(CWMoveVec[0], CWMoveVec[1], -vecCW[0], -vecCW[1], length_includes_head=True, fc='b', ec='b')
    # ax.arrow(CCWMoveVec[0], CCWMoveVec[1], vecCCW[0], vecCCW[1], length_includes_head=True, fc='r', ec='r')
    # ax.arrow(CCWMoveVec[0], CCWMoveVec[1], -vecCCW[0], -vecCCW[1], length_includes_head=True, fc='r', ec='r')
    # plt.plot(vecCW[0], vecCW[1], 'bx')
    # plt.plot(vecCCW[0], vecCCW[1], 'rx')
    # plt.plot([0], [0], 'kx')
    # plt.axes().set_aspect('equal')
    # plt.xlim(-10, 10)
    # plt.ylim(-10, 10)
    # plt.grid()
    # plt.show()
    return correctionVec


def calcInsideOutsideCutVertexDeltas(v, isOutside, toolCutDiameter):
    deltas = []
    for corner in verticesToCornersIter(np.roll(v, 1, axis=0)):
        deltas.append(calcCornerCorrectionVecForToolCutDiameter(corner,
                                                                toolCutDiameter,
                                                                isOutside))
    deltas = np.asarray(deltas)
    return deltas

def calcEdgeXIntercerptHorizontalLine(edge, y=0):
    if edge[0][1] == edge[1][1]:  ## SKIPS HORZONTAL EDGES
        return None    
    if edge[0][1] > edge[1][1]:
        hiVert = edge[0] 
        loVert = edge[1]
    else:
        hiVert = edge[1]
        loVert = edge[0]
    if y > hiVert[1]:
        return None
    if y < loVert[1]:
        return None
    xIntercept = np.interp(y, (loVert[1], hiVert[1]), (loVert[0], hiVert[0]))
    return xIntercept
