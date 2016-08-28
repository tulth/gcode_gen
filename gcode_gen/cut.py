from . import assembly
from . import number
from . import cmd
from . import shape
from . import vertex
from . import hg_coords

class DrillHole(assembly.Assembly):

    def _elab(self,
              xCenter, yCenter,
              zTop, zBottom,
              name="drillHole",
              plungeRate=None, zMargin=None, ):
        if plungeRate is None:
            plungeRate = self.cncCfg["defaultDrillingFeedRate"]
        if zMargin is None:
            zMargin = self.cncCfg["zMargin"]
        self += cmd.G0(z=self.cncCfg["zSafe"])
        self += cmd.G0(xCenter, yCenter)
        self += cmd.G0(z=zMargin + zTop)
        self += cmd.SetFeedRate(plungeRate)
        self += cmd.G1(z=zBottom)
        self += cmd.G1(z=zTop)
        self += cmd.G0(z=zMargin + zTop)
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
        self.transforms = hg_coords.TransformList() # already did transform, don't transform children
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
        self += cmd.G0(*self.correctedVertices[0][0:2])
        zTop = self.correctedVertices[0][2]
        zBottom = zTop - depth
        zStart = zTop + self.cncCfg["zMargin"]
        self += cmd.G0(z=zStart)
        zCutSteps = number.calcZSteps(zStart, zBottom, self.cncCfg["defaultDepthPerMillingPass"])
        for zCutStep in zCutSteps:
            if isFilled:
                self += shape.ConvexPolygonFill(self.correctedVertices, overlap=overlap).translate(z=zCutStep)
            if not isDogbone:
                self += shape.ConvexPolygonPerimeter(self.correctedVertices).translate(z=zCutStep)
            else:
                shp = shape.ConvexPolygonInsideDogbonePerimeter
                self += shp(self.vertices).translate(z=zCutStep)
        #     self += shape.ConvexPolygon(self.correctedVertices, isFilled, isCutPerimeter=isDogbone, overlap)
        #     self.last.translate(z=zCutStep)
        #     if not isDogbone:
        #         for corner in gcode_gen.vertex.verticesToCornersIter(np.roll(v, 1, axis=0)):
        #             vecCCW, vecCW = cornerToVectors(corner)
        #             diag = (vecCCW + vecCW)
        #             u_dogboneDir = -toUnitVec(diag)
                

    def calcOutlineCorrectedVertices(self, vertices, isOutline, toolCutDiameter):
        if isOutline is None:
            return vertices.copy()
        corr = vertex.calcInsideOutsideCutVertexDeltas(vertices, isOutline, toolCutDiameter)
        result = vertices + corr
        return result
            

