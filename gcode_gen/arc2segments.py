import numpy as np
from . import number
from numpy.linalg import norm

def arc2segments(p0, p1, r, segmentPerCircle=16, clockwise=True):
    assert clockwise == True  # ccw case not tested!
    center = _arc2segmentsFindCenter(p0, p1, r)
    p0RelativeToCenter = p0 - center
    p1RelativeToCenter = p1 - center
    unused, phi0 = cart2pol(p0RelativeToCenter)
    dphi = phiNorm(deltaPhi(p0RelativeToCenter, p1RelativeToCenter))
    circleFract = abs(dphi / 2 / np.pi)
    numSegmentsFloat = circleFract * segmentPerCircle
    numSegments = number.safeCeil(numSegmentsFloat)
    phiStep = dphi / numSegments
    results = []
    for segmentNum in range(numSegments):
        phi = phi0 - (segmentNum + 1) * phiStep
        point = pol2cart((r, phi)) + center
        results.append(point)
    xPoints = [p0[0]] + [result[0] for result in results]
    yPoints = [p0[1]] + [result[1] for result in results]
    return results

def _arc2segmentsFindCenter(p0, p1, r, clockwise=True):
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

def cart2pol(pt):
    x, y = pt
    r = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    phi = phiNorm(phi)
    return np.asarray((r, phi), dtype=float)

def pol2cart(polPt):
    r, phi = polPt
    x = r * np.cos(phi)
    y = r * np.sin(phi)
    return np.asarray((x, y), dtype=float)

def phiNorm(phi):
    while phi < 0:
        phi += 2 * np.pi
    while phi >= 2 * np.pi:
        phi -= 2 * np.pi
    return phi

def rotateVec90DegreesCounterClockwise(vec):
    result = vec.copy()
    result[0] = -vec[1]
    result[1] = vec[0]
    return result

def deltaPhi(u, v):
    """Given two vectors, return the angle between them, where positive angles correspond to clockwise motion"""
    phi = absDeltaPhi(u, v)
    if determinant(u, v) >= 0:
        phi += 2 * np.pi
    return phi
    # c = np.dot(u, v) / (norm(u) * norm(v)) # -> cosine of the angle
    # phi = np.arccos(np.clip(c, -1, 1))
    # return phi


def absDeltaPhi(u, v):
    """Given two vectors, return the ABS angle between them"""
    c = np.dot(u, v) / (norm(u) * norm(v)) # -> cosine of the angle
    phi = np.arccos(np.clip(c, -1, 1))
    return phi

def determinant(u, v):
    return u[0] * v[1] - u[1] * v[0]
