import numpy as np
from . import assembly
from . import number
from . import cmd
from . import shape
from . import vertex
from . import hg_coords

class DrillHole(assembly.Assembly):

    def _elab(self,
              depth,
              name="drillHole",
              plungeRate=None, zMargin=None, ):
        if plungeRate is None:
            plungeRate = self.cncCfg["defaultDrillingFeedRate"]
        if zMargin is None:
            zMargin = self.cncCfg["zMargin"]
        vert = np.asarray(((0,0,zMargin), (0,0,-depth), ), dtype=float)
        self.vertices = self.transforms.doTransform(vert)
        self += cmd.G0(z=self.cncCfg["zSafe"])
        self += cmd.G0(*self.vertices[0][:2])
        self += cmd.G0(z=self.vertices[0][2])
        originalFeedRate = self.cncCfg["lastFeedRate"]
        self += cmd.SetFeedRate(plungeRate)
        self += cmd.G1(z=self.vertices[1][2])
        self += cmd.G1(z=self.vertices[0][2])
        self += cmd.SetFeedRate(originalFeedRate)
        self += cmd.G0(z=self.cncCfg["zSafe"])


class ConvexPolygon(assembly.Assembly):
    """Cut a 2-d convex polygon shape to the specified depth.
    isOutline is None means follow the polygon vertices.  
    isOutline == True means compensate for toolCutDiameter for an OUTSIDE cut.
    isOutline == False means compensate for toolCutDiameter for an INSIDE cut.
    isDogbone is only valid for INSIDE cuts.
    """
    def _elab(self,
              vertices,
              depth,
              isFilled,
              isOutline,
              isDogbone=False,
              overlap=None,
              plungeRate=None,
              zMargin=None,
              ):
        self.vertices = vertex.standardizedConvexPolygonVertices(self.transforms.doTransform(vertices))
        self.depth = depth
        self.isOutline = isOutline
        self.isFilled = isFilled
        if isDogbone and ((isOutline is None) or isOutline):
            raise Exception("Dogbone is only valid when isOutline is False")
        if overlap is None:
            overlap = self.cncCfg["defaultMillingOverlap"]
        if plungeRate is None:
            plungeRate = self.cncCfg["defaultDrillingFeedRate"]
        if zMargin is None:
            zMargin = self.cncCfg["zMargin"]
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        #
        self.correctedVertices = self.calcOutlineCorrectedVertices(self.vertices,
                                                                   self.isOutline,
                                                                   toolCutDiameter)
        #
        self += cmd.G0(x=self.center[0], y=self.center[1])
        # zTop = self.correctedVertices[0][2]
        # zBottom = zTop - depth
        zStart = self.center[2] + zMargin
        self += cmd.G0(z=zStart)
        # zCutSteps = number.calcZSteps(zStart, zBottom, self.cncCfg["defaultDepthPerMillingPass"])
        zCutSteps = number.calcZSteps(zMargin, -depth, self.cncCfg["defaultDepthPerMillingPass"])
        # print("zCutSteps: {}".format(zCutSteps))
        for zCutStep in zCutSteps:
            if isFilled:
                self += shape.ConvexPolygonFill(self.correctedVertices, overlap=overlap).translate(z=zCutStep)
            if not isDogbone:
                self += shape.ConvexPolygonPerimeter(self.correctedVertices).translate(z=zCutStep)
            else:
                shp = shape.ConvexPolygonInsideDogbonePerimeter
                self += shp(self.vertices).translate(z=zCutStep)
        # already did transforms on verts, before passing to children so don't transform children!
        self += cmd.G0(x=self.center[0], y=self.center[1])
        self.transforms = hg_coords.TransformList() 
                

    def calcOutlineCorrectedVertices(self, vertices, isOutline, toolCutDiameter):
        if isOutline is None:
            return vertices.copy()
        corr = vertex.calcInsideOutsideCutVertexDeltas(vertices, isOutline, toolCutDiameter)
        result = vertices + corr
        return result
            

def Cylinder(depth,
             diameter,
             overlap=None,
             zMargin=None,
             segmentPerCircle=32):
    verts = shape.poly_circle_verts(segmentPerCircle)
    cyl = ConvexPolygon(vertices=verts,
                        depth=depth,
                        isFilled=True,
                        isOutline=False,
                        isDogbone=False,
                        overlap=overlap,
                        zMargin=zMargin,
                        ).scale(sx=diameter/2, sy=diameter/2)
    return cyl


def HexagonToDepth(depth,
                   faceToFace,
                   overlap=None,
                   isDogBone=True,
                   isFilled=True,
                   zMargin=None):
    verts = shape.HEXAGON
    scaleDiagonalToFactorFaceToFace = 1 / np.sqrt(3)
    scale = scaleDiagonalToFactorFaceToFace * faceToFace
    hgn = ConvexPolygon(vertices=verts,
                        depth=depth,
                        isFilled=isFilled,
                        isOutline=False,
                        isDogbone=isDogBone,
                        overlap=overlap,
                        zMargin=zMargin,
                        ).scale(sx=scale, sy=scale)
    return hgn
    
    
