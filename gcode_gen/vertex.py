import numpy as np
# from numpy.linalg import norm
import numpy.linalg
import itertools
import operator
from . import number
from .debug import DBGP

ZERO_VERTS = np.asarray(((0, 0, 0), ), dtype=float)


def verticesToCornersIter(vertices):
    return edgesToCornersIter(verticesToEdgesIter(vertices))


def verticesToEdgesIter(vertices):
    return number.loopPairsIter(vertices)


def edgesToCornersIter(edges):
    return number.loopPairsIter(edges)


def getSignedAreaX2(vertices):
    xCoords = vertices[:, 0]
    yCoords = vertices[:, 1]
    return np.dot(xCoords, np.roll(yCoords, 1)) - np.dot(yCoords, np.roll(xCoords, 1))


def getOrientation(vertices):
    """returns 0 if collinear, 1 if clockwise, -1 if counter clockwise"""
    return np.sign(getSignedAreaX2(vertices))


def isClockwiseVertices(vertices):
    return getOrientation(vertices) == 1


def isCounterClockwiseVertices(vertices):
    return getOrientation(vertices) == -1


def edgeEndPointCrossproductsIter(vertices):
    for edge in verticesToEdgesIter(vertices):
        print(edge)
        print(edge[0][0]*edge[1][1] - edge[1][0]*edge[0][1])
        yield np.cross(edge[0], edge[1])


def getCornerVectors(vertices):
    vec0s = np.roll(vertices, 1, axis=0) - vertices
    vec1s = np.roll(vertices, -1, axis=0) - vertices
    return vec0s, vec1s

def getCornerCrossproducts(vertices):
    return np.cross(*getCornerVectors(vertices))


def getOrientations(vertices):
    """returns 0 if collinear, 1 if clockwise, -1 if counter clockwise"""
    return np.sign(getCornerCrossproducts(vertices))
    

def isConvex(vertices):
    orientations = getOrientations(vertices)
    # DBGP(orientations)
    ##
    hasClockwiseOrientations = np.any(orientations > 0)
    hasCounterClockwiseOrientations = np.any(orientations < 0)
    return not (hasClockwiseOrientations and hasCounterClockwiseOrientations)


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

def norm(vec):
    return numpy.linalg.norm(vec)

def toUnitVec(vec):
    return vec / norm(vec)


def toUnitVecs(vecs):
    """0 length vectors return zero length vectors!"""
    mags = np.sqrt((vecs ** 2).sum(-1))
    result = np.empty_like(vecs)
    div0Indices = np.where(mags == 0)
    nonDiv0Indices = np.where(mags != 0)
    result[div0Indices] = vecs[div0Indices]
    result[nonDiv0Indices] = vecs[nonDiv0Indices] / (mags[nonDiv0Indices])[..., np.newaxis]
    return result


def calcCornerCorrectionVecForToolCutDiameter(corner, toolCutDiameter, isOutsideCorrection):
    """ASSUMES corner is a from a vertex list that conforms to standardizedConvexPolygonVertices!"""
    vecCCW, vecCW = cornerToVectors(corner)
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


def getBounds(vertices):
    assert isinstance(vertices, np.ndarray)
    if vertices.shape[1] not in (2, ):
        raise Exception("boundingBox argument must be 2 dimensional vertex list")
    bounds = np.asarray([(np.min(vertices[:, dimNum]), np.max(vertices[:, dimNum]), ) for dimNum in range(vertices.shape[1])])
    return bounds

def convertBoundsToBox(bounds):
    return np.asarray((
        (bounds[0][0], bounds[1][0], ),
        (bounds[0][1], bounds[1][0], ),
        (bounds[0][1], bounds[1][1], ),
        (bounds[0][0], bounds[1][1], ),
        ))

def getBoundingBox(vertices):
    bounds = getBounds(vertices)
    return convertBoundsToBox(bounds)

def getScaledBounds(vertices, scaleFactor=1.1):
    bounds = getBounds(vertices)
    sizes = np.asarray([bounds[dimNum][1] - bounds[dimNum][0] for dimNum in range(2)])
    scaledSizes = sizes * scaleFactor
    deltas = (scaledSizes - sizes) / 2.0
    scaledBounds = np.asarray((
        ((bounds[0][0] - deltas[0]),
         (bounds[0][1] + deltas[0]), ),
        ((bounds[1][0] - deltas[1]),
         (bounds[1][1] + deltas[1]), ),
        ))
    return scaledBounds


def getScaledBoundingBox(vertices, scaleFactor=1.1):
    return convertBoundsToBox(getScaledBounds(vertices, scaleFactor))


def isOnEdge(edge, vert):
    if not(edge[1][0] <= max(edge[0][0], vert[0])):
        return False
    if not(edge[1][0] >= min(edge[0][0], vert[0])):
        return False
    if not(edge[1][1] <= max(edge[0][1], vert[1])):
        return False
    if not(edge[1][1] >= min(edge[0][1], vert[1])):
        return False
    return True
    # if (edge[1][0] <= max(edge[0][0], vert[0]) and edge[1][0] >= min(edge[0][0], vert[0]) and
    #     edge[1][1] <= max(edge[0][1], vert[1]) and edge[1][1] >= min(edge[0][1], vert[1])):
    #     return True
    # else:
    #     return False


def isEdgeIntersect(edge0, edge1):
    left = max(min(edge0[0][0], edge0[1][0]), min(edge1[0][0], edge1[1][0]))
    right = min(max(edge0[0][0], edge0[1][0]), max(edge1[0][0], edge1[1][0]))
    top = max(min(edge0[0][1], edge0[1][1]), min(edge1[0][1], edge1[1][1]))
    bottom = min(max(edge0[0][1], edge0[1][1]), max(edge1[0][1], edge1[1][1]))

    if top > bottom or left > right:
        return False
    else:
        return True
    
# # Below did not work
# def isEdgeIntersect(edge0, edge1):
#     p1 = edge0[0]
#     q1 = edge0[1]
#     p2 = edge1[0]
#     q2 = edge1[1]
#     o1 = getOrientation(np.asarray((p1, q1, p2)))
#     o2 = getOrientation(np.asarray((p1, q1, q2)))
#     o3 = getOrientation(np.asarray((p2, q2, p1)))
#     o4 = getOrientation(np.asarray((p2, q2, q1)))
#     # general case
#     if (o1 != o2) and (o3 != o4):
#         return True
#     # Special Cases
#     # p1, q1 and p2 are colinear and p2 lies on segment p1q1
#     if (o1 == 0) and isOnEdge(np.asarray((p1, p2)), q1):
#         return True
#     # p1, q1 and p2 are colinear and q2 lies on segment p1q1
#     if (o2 == 0) and isOnEdge(np.asarray((p1, q2)), q1):
#         return True
#     # p2, q2 and p1 are colinear and p1 lies on segment p2q2
#     if (o3 == 0) and isOnEdge(np.asarray((p2, p1)), q2):
#         return True
#      # p2, q2 and q1 are colinear and q1 lies on segment p2q2
#     if (o4 == 0) and isOnEdge(np.asarray((p2, q1)), q2):
#         return True
#     # else false
#     return False

def isSimple(vertices):
    numEdges = len(vertices)
    edges = tuple(verticesToEdgesIter(vertices))
    for edgeIndexPair in itertools.combinations(range(len(vertices)), 2):
        if ((edgeIndexPair[0] + 1) % numEdges) == edgeIndexPair[1]:
            # print("adjacent")
            continue
        elif ((edgeIndexPair[0] - 1) % numEdges) == edgeIndexPair[1]:
            # print("adjacent")
            continue
        else:
            #DBGP(edgeIndexPair)
            #DBGP(edges[edgeIndexPair[0]])
            #DBGP(edges[edgeIndexPair[1]])
            #print("** NOT adjacent **")
            if (isEdgeIntersect(edges[edgeIndexPair[0]], edges[edgeIndexPair[1]])):
                #print("** Intersected! **")
                return False
    return True

