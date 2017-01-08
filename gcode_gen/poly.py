#!/usr/bin/env python
"""Polygon library"""
import numpy as np
from numpy.linalg import norm
from . import number
from . import vertex
from .debug import DBGP

class PolygonResizeError(Exception):
    pass

class Polygon(object):
    
    def __init__(self, vertices, zVal=None, name=None):
        self.name = name
        self.vertices = np.asarray(vertices, dtype=np.float)
        if self.vertices.shape[1] not in (2, 3):
            raise Exception("Polygon must be 2 or 3 dimensional")
        if self.vertices.shape[1] == 3:
            self._convert3dVerticesTo2d()
            if zVal is not None and not number.floatEq(zVal, self.zVal):
                errStrFmt = "Polygon must be coplanar, zVal argument was not floatEq to 3d verteces zVal={}"
                raise Exception(errStrFmt.format(zVal, self.zVal))
        else:
            self.zVal = zVal
        if self.vertices.shape[0] < 3:
            raise Exception("Polygon have at least 3 vertices")
        self.clearProps()
        
    def clearProps(self, ):
        self._counterClockwise = None  # calculated on demand
        self._convex = None  # calculated on demand
        self._simple = None  # calculated on demand
        self._boundingBox = None  # calculated on demand
        self._orientations = None  # calculated on demand
        
    def _convert3dVerticesTo2d(self):
        self.zVal = self.vertices[0, 2]
        for vertNum, vert in enumerate(self.vertices[1:]):
            thisZ = vert[2]
            if not number.floatEq(self.zVal, thisZ):
                errStrFmt = "Polygon must be coplanar, vertex[0][2]={} was not floatEq to vertex[{}][2]={}"
                raise Exception(errStrFmt.format(self.zVal, vertNum, thisZ))
        self.vertices = self.vertices[:, 0:2]
        
    @property
    def isCounterClockwise(self, ):
        if self._counterClockwise is None:
            self._counterClockwise = vertex.isCounterClockwiseVertices(self.vertices)
        return self._counterClockwise

    @property
    def isClockwise(self, ):
        return not self.isCounterClockwise
        
    @property
    def orientations(self, ):
        if self._orientations is None:
            self._orientations = vertex.getOrientations(self.vertices)
        return self._orientations
        
    @property
    def isConvex(self, ):
        if self._convex is None:
            self._convex = vertex.isConvex(self.vertices)
        return self._convex
        
    @property
    def boundingBox(self, ):
        if not self._boundingBox:
            self._boundingBox = vertex.getBoundingBox(self.vertices)
        return self._boundingBox
        
    @property
    def isSimple(self, ):
        if self._simple is None:
            if self.isConvex:
                self._simple = True
            else:
                self._simple = vertex.isSimple(self.vertices)
        return self._simple
        
    def __str__(self, ):
        return "2d-Vertices: {}, zVal={}".format(self.vertices, self.zVal)

    def plot(self, show=True, figure=True, color='r', title=None):
        import matplotlib.pyplot as plt
        if figure:
            plt.figure()
        if title is not None:
            plt.title(title)
        elif self.name is not None:
            plt.title(self.name)
        for edge in vertex.verticesToEdgesIter(self.vertices):
            xPoints = [point[0] for point in edge]
            yPoints = [point[1] for point in edge]
            plt.plot(xPoints, yPoints, marker='o', color=color, ls='-')
        plt.grid()
        plt.axis(vertex.getScaledBounds(self.vertices).flatten())
        plt.axes().set_aspect('equal')
        if show:
            plt.show()

    def shrinkPoly(self, amount, name=None):
        if not self.isSimple:
            raise PolygonResizeError("Growing/shrinking a non-simple polygon is not supported")
        prevVecs, nextVecs = vertex.getCornerVectors(self.vertices)
        #DBGP(prevVecs)
        #DBGP(nextVecs)
        u_prevVecs = vertex.toUnitVecs(prevVecs)
        u_nextVecs = vertex.toUnitVecs(nextVecs)
        u_nextPerpCwVecs = np.empty_like(u_nextVecs)
        u_nextPerpCwVecs[:, 0] = u_nextVecs[:, 1]
        u_nextPerpCwVecs[:, 1] = -u_nextVecs[:, 0]
        #DBGP(u_prevVecs)
        #DBGP(u_nextVecs)
        u_correctionVecs = vertex.toUnitVecs(u_prevVecs + u_nextVecs)
#        u_correctionVecs *= self.orientations.reshape(len(self.vertices), 1)
        # if self.isCounterClockwise:
        #     u_correctionVecs *= -1
        # DBGP(u_correctionVecs)
        # angles = (np.arcsin(np.cross(u_prevVecs, u_nextVecs)) * 180 / np.pi)
        # halfAngles = angles / 2
        # correctionVec
        # if self.isCounterClockwise:
        #     angles = -angles
        # DBGP(angles)
        reciprocalCorrectionVecLens = np.cross(u_nextVecs, u_correctionVecs) / amount
        if self.isClockwise:
            reciprocalCorrectionVecLens *= -1
        #DBGP(reciprocalCorrectionVecLens)
        # DBGP(np.arcsin(np.cross(u_prevVecs, u_nextVecs))/np.pi * 180)
        # dotProds = (u_prevVecs * u_nextVecs).sum(1)
        # correctionMags = amount * np.reciprocal(np.sqrt(np.ones(dotProds.shape) - dotProds)**2)
        # DBGP(correctionMags)
        if self.isCounterClockwise:
            u_nextPerpCwVecs = -u_nextPerpCwVecs
        # correctionMags = correctionMags * orients
        # correctionMags = correctionMags.reshape(len(self.vertices), 1)
        # correctionVecs = u_prevVecs + u_nextVecs
        # correctionVecsLengths = np.sqrt((correctionVecs * correctionVecs).sum(axis=1))
        # DBGP(correctionVecsLengths)
        collinearIndices = np.where(reciprocalCorrectionVecLens == 0)
        # DBGP(collinearIndices)
        # DBGP(correctionVecs)
        # DBGP(collinearIndices)
        # DBGP(correctionVecs[collinearIndices])
        # DBGP(u_nextPerpCwVecs[collinearIndices])
        # DBGP(correctionVecs)
        # DBGP(correctionMags)
        # correctionMags = correctionMags.reshape(len(self.vertices), 1)
        correctionVecs = u_correctionVecs * np.reciprocal(reciprocalCorrectionVecLens.reshape(len(self.vertices), 1))
        correctionVecs[collinearIndices] = amount * u_nextPerpCwVecs[collinearIndices]
        # DBGP(correctionVecs)
        #
        newVerts = self.vertices + correctionVecs
        #
        newName = name
        if (newName is None) and (self.name is not None):
            newName = "{}_shrink({})".format(self.name, amount)
        result = Polygon(newVerts, zVal=self.zVal, name=newName)
        if not result.isSimple:
            # print("Error: ", result.vertices)
            self.plot(figure=True, show=False, color='b')
            result.plot(figure=False, show=True)
            #print("simple ", vertex.isSimple(result.vertices))
            raise PolygonResizeError("Growing/shrinking resulted in a non-simple polygon.")
        return result

    def growPoly(self, amount, name=None):
        return self.shrinkPoly(-amount, name)
