#!/usr/bin/env python
"""Polygon library"""
import numpy as np
from numpy.linalg import norm
from . import number
from . import vertex
from . import poly
from .debug import DBGP

# FIXME! technically this poly should be filled!!!
# why? consider the case where the touchup tool is much much smaller than the orig (coarse) tool diameter
def getOutlineDogBoneTouchUpInsideCornersPolys(origPoly, origToolDiameter, touchUpToolDiameter):
    assert touchUpToolDiameter <= origToolDiameter
    expandedOrigToolPoly = origPoly.growPoly(origToolDiameter / 2)
    expandedTouchUpToolPoly = origPoly.growPoly(touchUpToolDiameter / 2)
    for vertIdx in expandedOrigToolPoly.getInsideCornerIndices():
        baseVert = origPoly.vertices[vertIdx]
        expandedOrigToolVert = expandedOrigToolPoly.vertices[vertIdx]
        expandedTouchUpToolVert = expandedTouchUpToolPoly.vertices[vertIdx]
        origToolCornerVerts = expandedOrigToolPoly.getCornerVertsForIndex(vertIdx)
        touchUpToolCornerVerts = expandedTouchUpToolPoly.getCornerVertsForIndex(vertIdx)
        # debug.DBGP(origToolCornerVerts)
        cornerOrientation = vertex.getOrientation(origToolCornerVerts)
        # debug.DBGP(cornerOrientation)
        # vec0, vec1 = vertex.cornerToVectors(corner)
        vec0, vec1 = (origToolCornerVerts[1] - origToolCornerVerts[0], origToolCornerVerts[-1] - origToolCornerVerts[0], )
        diagonal = (vertex.toUnitVec(vec0) + vertex.toUnitVec(vec1))
        moveDirection = -vertex.toUnitVec(diagonal)
        moveAmount = touchUpToolDiameter / 2
        dogbonePoint = baseVert - moveDirection * moveAmount
        dogbonedInnerVerts = []
        edgeCorrectionMag = (origToolDiameter - touchUpToolDiameter) / 2 # THIS IS AN OVERESTIMATION!
        edgeCorrectionVec0 = edgeCorrectionMag * vertex.toUnitVec(touchUpToolCornerVerts[-1] - expandedTouchUpToolVert)
        dogbonedInnerVerts.append(expandedTouchUpToolVert + edgeCorrectionVec0)
        #dogbonedInnerVerts.append(touchUpToolCornerVerts[-1])
        dogbonedInnerVerts.append(expandedTouchUpToolVert)
        dogbonedInnerVerts.append(dogbonePoint)
        dogbonedInnerVerts.append(expandedTouchUpToolVert)
        edgeCorrectionVec1 = edgeCorrectionMag * vertex.toUnitVec(touchUpToolCornerVerts[1] - expandedTouchUpToolVert)
        dogbonedInnerVerts.append(expandedTouchUpToolVert + edgeCorrectionVec1)
        dogbonedInnerPoly = poly.Polygon(dogbonedInnerVerts)
        yield dogbonedInnerPoly

# below is an idea that didn't work out - trying to make a touchup poly that could eventually be filled.
# this concept ran into problems with it shrinking too small for current planned tool sizes
# def getOutlineDogBoneTouchUpInsideCornersPolys(origPoly, origToolDiameter, touchUpToolDiameter):
#     assert touchUpToolDiameter <= origToolDiameter
#     expandedOrigToolPoly = origPoly.growPoly(origToolDiameter / 2)
#     for vertIdx in expandedOrigToolPoly.getInsideCornerIndices():
#         baseVert = origPoly.vertices[vertIdx]
#         expandedOrigToolVert = expandedOrigToolPoly.vertices[vertIdx]
#         origPolyCornerVerts = origPoly.getCornerVertsForIndex(vertIdx)
#         uvec0, uvec1 = (vertex.toUnitVec(origPolyCornerVerts[1] - origPolyCornerVerts[0]),
#                         vertex.toUnitVec(origPolyCornerVerts[-1] - origPolyCornerVerts[0]), )
#         DBGP((uvec0, uvec1))
#         adjustMag = max(origToolDiameter / 2 , touchUpToolDiameter * 1.01)  # prevent zero length poly legs
#         DBGP(adjustMag)
#         touchUpToolPolyVerts = (origPolyCornerVerts[0],
#                                 origPolyCornerVerts[0] + adjustMag * uvec0,
#                                 origPolyCornerVerts[0] + adjustMag * uvec1, )
#         touchUpToolPoly = poly.Polygon(touchUpToolPolyVerts)
#         touchUpToolPoly.plot(figure=True, show=False, color='r')
#         touchUpToolPoly = poly.Polygon(touchUpToolPolyVerts).shrinkPoly(touchUpToolDiameter / 2)
#         touchUpToolPoly.plot(figure=False, show=False, color='g')
#         origPoly.plot(figure=False, show=False, color='k')
#         expandedOrigToolPoly.plot(figure=False, show=True, color='b')
#         DBGP(origPoly.getCornerVertsForIndex(vertIdx))
#         DBGP(touchUpToolPolyVerts)
#         DBGP(touchUpToolPoly)
#         expandedTouchUpToolVert = touchUpToolPoly.vertices[0]
#         origToolCornerVerts = expandedOrigToolPoly.getCornerVertsForIndex(vertIdx)
#         touchUpToolCornerVerts = touchUpToolPoly.getCornerVertsForIndex(vertIdx)
#         # debug.DBGP(origToolCornerVerts)
#         cornerOrientation = vertex.getOrientation(origToolCornerVerts)
#         # debug.DBGP(cornerOrientation)
#         # vec0, vec1 = vertex.cornerToVectors(corner)
#         vec0, vec1 = (origToolCornerVerts[1] - origToolCornerVerts[0], origToolCornerVerts[-1] - origToolCornerVerts[0], )
#         diagonal = (vertex.toUnitVec(vec0) + vertex.toUnitVec(vec1))
#         moveDirection = -vertex.toUnitVec(diagonal)
#         moveAmount = touchUpToolDiameter / 2
#         dogbonePoint = baseVert - moveDirection * moveAmount
#         dogbonedInnerVerts = []
#         # edgeCorrectionMag = origToolDiameter / 2 # THIS IS AN OVERESTIMATION!
#         edgeCorrectionMag = 1
#         edgeCorrectionVec0 = edgeCorrectionMag * vertex.toUnitVec(touchUpToolCornerVerts[-1] - expandedTouchUpToolVert)
#         #dogbonedInnerVerts.append(expandedTouchUpToolVert + edgeCorrectionVec0)
#         dogbonedInnerVerts.append(touchUpToolCornerVerts[-1])
#         dogbonedInnerVerts.append(expandedTouchUpToolVert)
#         dogbonedInnerVerts.append(dogbonePoint)
#         dogbonedInnerVerts.append(expandedTouchUpToolVert)
#         edgeCorrectionVec1 = edgeCorrectionMag * vertex.toUnitVec(touchUpToolCornerVerts[1] - expandedTouchUpToolVert)
#         #dogbonedInnerVerts.append(expandedTouchUpToolVert + edgeCorrectionVec1)
#         dogbonedInnerVerts.append(touchUpToolCornerVerts[1])
#         dogbonedInnerPoly = poly.Polygon(dogbonedInnerVerts)
#         yield dogbonedInnerPoly
