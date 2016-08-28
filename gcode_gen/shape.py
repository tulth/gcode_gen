import numpy as np
from . import assembly
from . import number
from . import cmd
from . import hg_coords
from . import vertex
from numpy.linalg import norm


def poly_circle_verts(segmentPerCircle=32):
    spc = segmentPerCircle
    assert spc >= 3
    phi0 = np.pi / 2
    if spc % 2 == 0:
        phi0 += np.pi / spc
    vertList = [(np.cos(phi + phi0), np.sin(phi + phi0)) for phi in np.linspace(0, 2 * np.pi, spc, endpoint=False)]
    return np.asarray(vertList, dtype=float)

EQUILATERAL_TRIANGLE = poly_circle_verts(3)
SQUARE = poly_circle_verts(4)
HEXAGON = poly_circle_verts(6)


class BaseShape(assembly.Assembly):
    pass
        
class ConvexPolygonPerimeter(BaseShape):
    
    def _elab(self, vertices, ):
        self.vertices = vertex.standardizedConvexPolygonVertices(self.transforms.doTransform(vertices))
        for v in self.vertices:
            self += cmd.G1(*v)
        self += cmd.G1(*self.vertices[0])
    
class ConvexPolygonInsideDogbonePerimeter(BaseShape):
    
    def _elab(self, vertices):
        self.vertices = vertex.standardizedConvexPolygonVertices(self.transforms.doTransform(vertices))
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        corr = vertex.calcInsideOutsideCutVertexDeltas(self.vertices,
                                                       isOutside=False,
                                                       toolCutDiameter=toolCutDiameter)
        self.insideVertices = self.vertices + corr
        for baseVert, corner in zip(self.vertices,
                                vertex.verticesToCornersIter(np.roll(self.insideVertices, 1, axis=0))):
            insideVert = corner[0][1]
            self += cmd.G1(*insideVert)
            vecCCW, vecCW = vertex.cornerToVectors(corner)
            diagonal = (vecCCW + vecCW)
            moveDirection = -vertex.toUnitVec(diagonal)
            moveAmount = toolCutDiameter / 2
            dogBonePoint = baseVert - moveDirection * moveAmount
            self += cmd.G1(*(dogBonePoint))
            self += cmd.G1(*insideVert)
        self += cmd.G1(*self.insideVertices[0])
    
class ConvexPolygonFill(BaseShape):
    
    def _elab(self, vertices, overlap=None, ):
        self.vertices = vertex.standardizedConvexPolygonVertices(self.transforms.doTransform(vertices))
        if overlap is None:
            overlap = self.cncCfg["defaultMillingOverlap"]
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        botLeftIdx = 0
        topIdx = vertex.findTopVertexIdx(self.vertices)
        ySteps = number.calcFillSteps(self.vertices[botLeftIdx][1], self.vertices[topIdx][1],
                                      toolCutDiameter, overlap)
        xStarts, xStops = [], []
        for yStep in ySteps:
            xInts = []
            for edge in vertex.verticesToEdgesIter(self.vertices):
                xInt = vertex.calcEdgeXIntercerptHorizontalLine(edge, yStep)
                if xInt is not None:
                    xInts.append(xInt)
                # print("yStep: {} xInt:{} edge: {}".format(yStep, xInt, edge))
            xStarts.append(min(xInts))
            xStops.append(max(xInts))
            #print("yStep: {} xStart: {}, xStop: {}".format(yStep, xStarts[-1], xStops[-1]))
        self += cmd.G0(*self.vertices[botLeftIdx])
        for xCoord, yCoord in number.fillWalkIter(ySteps, xStarts, xStops):
            self += cmd.G1(x=xCoord, y=yCoord)
        # import sys
        # sys.exit()
        # vertGroups = {"l": self.vertices[0:(topIdx+1), :],
        #               "r": np.concatenate((self.vertices[topIdx:, :], self.vertices[:1, :]))}
        # xStepsGroups = {}
        # for groupName in vertGroups:
        #     vertGroup = vertGroups[groupName]
        #     xParams = vertGroup[:, 0] # [vert[0] for vert in vertGroup]
        #     yParams = vertGroup[:, 1] # [vert[1] for vert in vertGroup]
        #     print("{} xParams: {} yParams: {}".format(groupName, xParams, yParams))
        #     if groupName == "l":
        #         xSteps = np.interp(ySteps, yParams, xParams)
        #     else:
        #         xSteps = np.interp(ySteps, np.flipud(yParams), xParams)
        #     xStepsGroups[groupName] = xSteps
        # print(xStepsGroups)
        # self += cmd.G0(*self.vertices[botLeftIdx])
        # for xCoord, yCoord in number.fillWalkIter(ySteps, xStepsGroups["l"], xStepsGroups["r"]):
        #     self += cmd.G1(x=xCoord, y=yCoord)
            
def plotpoints(points, *args, **kwargs):
    import matplotlib.pyplot as plt
    plt.figure()
    for edge in vertex.verticesToEdgesIter(points):
        xPoints = [point[0] for point in edge]
        yPoints = [point[1] for point in edge]
        plt.plot(xPoints, yPoints, *args, **kwargs)
    plt.grid()
    plt.axes().set_aspect('equal')
