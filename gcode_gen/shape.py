import numpy as np
from . import assembly
from . import number
from . import cmd
from . import hg_coords

HEXAGON = np.asarray(
    # ((0,    0, ),
    #  (1,    0, ),       
    #  (1.5,  np.sqrt(3)/2, ),
    #  (1,    np.sqrt(3), ),
    #  (0,    np.sqrt(3), ),
    #  (-0.5, np.sqrt(3)/2, ), 
    # ((-0.5,    -np.sqrt(3)/2, ),
    #  ( 0.5,    -np.sqrt(3)/2, ),
    #  ( 1,      0, ),       
    #  ( 0.5,     np.sqrt(3)/2, ),
    #  (-0.5,     np.sqrt(3)/2, ),
    #  (-1,      0, ),       
    # )) / (np.sqrt(3)/2) / 2
    ((-np.sqrt(3)/6,    -1/2, ),
     ( np.sqrt(3)/6,    -1/2, ),
     ( np.sqrt(3)/3,     0, ),       
     ( np.sqrt(3)/6,     1/2, ),
     (-np.sqrt(3)/6,     1/2, ),
     (-np.sqrt(3)/3,     0, ),       
    ))

SQUARE = np.asarray(
    ((-0.5,   -0.5, ),
     ( 0.5,   -0.5, ),       
     ( 0.5,    0.5, ),
     (-0.5,    0.5, ),
    ))

EQUILATERAL_TRIANGLE = np.asarray(
    ((0,    0, ),
     (1,    0, ),       
     (.5,   np.sqrt(2)/2, ),
    ))


from . import arc2segments
def poly_circle_verts(segmentPerCircle=32):
    return np.asarray(arc2segments.arc2segments(np.asarray((0, 0.5)),
                                                np.asarray((0, -0.5)),
                                                0.5, segmentPerCircle, clockwise=True) +
                      arc2segments.arc2segments(np.asarray((0, -0.5)),
                                                np.asarray((0, 0.5)),
                                                0.5, segmentPerCircle, clockwise=True)
                      )

class BaseShape(assembly.Assembly):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.transforms = hg_coords.TransformList()
        
        
class ConvexPolygon(BaseShape):
    
    def doFill(self, vertices, toolCutDiameter, overlap=None, ):
        botLeftIdx = number.findBotLeftVertexIdx(vertices)
        topIdx = None
        for idx, vertex in enumerate(vertices):
            if topIdx is None or vertex[1] > vertices[topIdx][1]:
                topIdx = idx
        ySteps = number.calcFillSteps(vertices[botLeftIdx][1], vertices[topIdx][1], toolCutDiameter, overlap)
        faceGroups = {"left": [], "right": []}
        curGroup = "left"
        for num in range(len(vertices)):
            idx = (num + botLeftIdx) % len(vertices)
            prevIdx = (idx - 1) % len(vertices)
            faceGroups[curGroup].append(idx)
            if idx == topIdx:
                curGroup = "right"
                faceGroups[curGroup].append(idx)
        faceGroups[curGroup].append(botLeftIdx)
        xSteps2Lists = []
        for faceGroupName in faceGroups:
            faceGroup = faceGroups[faceGroupName]
            xParams = [vertices[idx][0] for idx in faceGroup]
            yParams = [vertices[idx][1] for idx in faceGroup]
            assert number.monotone(yParams)
            if number.monotone_decreasing(yParams):
                xParams = list(reversed(xParams))
                yParams = list(reversed(yParams))
            xSteps = np.interp(ySteps, yParams, xParams)
            xSteps2Lists.append(xSteps)
        xStartSteps = [min(x0, x1) for x0, x1 in zip(xSteps2Lists[0], xSteps2Lists[1], )]
        xStopSteps = [max(x0, x1) for x0, x1 in zip(xSteps2Lists[0], xSteps2Lists[1], )]
        self += cmd.G0(*vertices[botLeftIdx])
        yIter = iter(ySteps)
        for xCoord, yCoord in zip(number.serpentIter(xStartSteps, xStopSteps), number.twiceIter(ySteps)):
            self += cmd.G1(x=xCoord, y=yCoord)
    
    def doPerimeter(self, vertices, toolCutDiameter):
        for vertex in vertices:
            self += cmd.G1(*vertex)
        self += cmd.G1(*vertices[0])
    
    def _elab(self, vertices, isFilled, overlap=None, ):
        workVerts = self.transforms.doTransform(vertices)
        assert not np.any(workVerts[:, -1])
        workVerts = workVerts[:, :-1]
        if overlap is None:
            overlap = self.cncCfg["defaultMillingOverlap"]
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        if not number.isClockwiseVertexList(workVerts):
            workVerts = np.flipud(workVerts)
        if isFilled:
            self.doFill(workVerts, toolCutDiameter, overlap)
        self.doPerimeter(workVerts, toolCutDiameter)
        
def plotpoints(points):
    import matplotlib.pyplot as plt
    plt.figure()
    xPoints = [point[0] for point in points]
    yPoints = [point[1] for point in points]
    plt.plot(xPoints, yPoints, 'ro')
    plt.grid()
    plt.axes().set_aspect('equal')
    plt.show()
