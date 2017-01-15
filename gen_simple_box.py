#!/usr/bin/env python
"""Generates gcode that uses nomad 883 to create a simple tab insert box"""
import sys
import argparse
import logging
import numpy as np
import gcode_gen as gc
import common
from functools import partial
import itertools
import rect_pack

#FAST_SCAD = True
FAST_SCAD = False
SCAD_SHOW_WORKPIECE = True
#SCAD_SHOW_WORKPIECE = False
SCAD_SHOW_RPI3_CCA = SCAD_SHOW_WORKPIECE

EDGE_MARGIN = 8

log = logging.getLogger()

def initFromDict(d):
    self = d.pop('self')
    for n, v in d.items():
        setattr(self, n, v)

class SimpleBoxBaseFace(gc.hg_coords.Transformable):
    def __init__(self,
                 name,
                 interiorX,
                 interiorY,
                 workpieceDepth,
                 tabLength,
                 postTabThickness,
                 coarseToolCutDiameter,
                 fineToolCutDiameter,
                 workpieceExtraCutDepth=0.8,
                 customFaceCut=None,
                 ):
        initFromDict(locals())
        self.boxExteriorX = self.interiorX + 2 * (workpieceDepth + postTabThickness)
        self.boxExteriorY = self.interiorY + 2 * (workpieceDepth + postTabThickness)
        self.baseOutlineVerts = np.asarray([[-self.EOX(), -self.EOY()],
                                            [self.EOX(), -self.EOY()],
                                            [self.EOX(), self.EOY()],
                                            [-self.EOX(), self.EOY()],
                                            ])

    @property
    def cutDepth(self, ):
        return self.workpieceDepth + self.workpieceExtraCutDepth

    def EOX(self, ): # exterior offset X
        raise NotImplementedError()

    def EOY(self, ): # exterior offset X
        raise NotImplementedError()

    def dogboneFineOutlineCleanup(self, asm):
        for touchUpPoly in gc.dogbone.getOutlineDogBoneTouchUpInsideCornersPolys(
                self.outlinePoly,
                self.coarseToolCutDiameter,
                self.fineToolCutDiameter, ):
            asm += gc.cut.PolygonCut(touchUpPoly, depth=self.cutDepth)
            # touchUpPoly.plot(figure=True, show=False, color='r')
            # self.outlinePoly.plot(figure=False, show=False, color='k')
            # self.expandedOutlinePoly.plot(figure=False, show=True, color='b')

    def addCoarseCuts(self, asm):
        self.customFaceCutCoarse(asm)
        asm += gc.cut.PolygonCut(self.expandedOutlinePoly, self.cutDepth)

    def addFineCuts(self, asm):
        self.customFaceCutFine(asm)

    def customFaceCutCoarse(self, asm):
        if self.customFaceCut is not None:
            if "Coarse" in self.customFaceCut:
                for poly in self.customFaceCut["Coarse"]:
                    asm += gc.cut.PolygonCut(poly, self.cutDepth)
                    asm.last().translate(-self.interiorX/2, -self.interiorY/2, )

    def customFaceCutFine(self, asm):
        if self.customFaceCut is not None:
            if "Fine" in self.customFaceCut:
                for poly in self.customFaceCut["Fine"]:
                    asm += gc.cut.PolygonCut(poly, self.cutDepth)
                    asm.last().translate(-self.interiorX/2, -self.interiorY/2, )


class FrontBackBoxFace(SimpleBoxBaseFace):
    def __init__(self,
                 name,
                 interiorX,
                 interiorY,
                 workpieceDepth,
                 tabLength,
                 postTabThickness,
                 coarseToolCutDiameter,
                 fineToolCutDiameter,
                 footWidth,
                 footDepth,
                 workpieceExtraCutDepth=0.8,
                 customFaceCut=None,
                 ):
        super().__init__(name,
                         interiorX,
                         interiorY,
                         workpieceDepth,
                         tabLength,
                         postTabThickness,
                         coarseToolCutDiameter,
                         fineToolCutDiameter,
                         workpieceExtraCutDepth,
                         customFaceCut,
                         )
        self.footWidth = footWidth
        self.footDepth = footDepth
        self.outlineVerts = self.baseOutlineVerts.copy()
        self.outlineVerts[0] += np.asarray((0, -self.footDepth))
        self.outlineVerts[1] += np.asarray((0, -self.footDepth))
        newVerts = []
        newVerts.append(self.outlineVerts[0] + np.asarray((self.footWidth, 0)))
        newVerts.append(newVerts[-1] + np.asarray((0, +self.footDepth)))
        newVerts.append(self.outlineVerts[1] + np.asarray((-self.footWidth, self.footDepth)))
        newVerts.append(newVerts[-1] + np.asarray((0, -self.footDepth)))
        self.outlineVerts = np.asarray([self.outlineVerts[0].tolist()] + newVerts + self.outlineVerts[1:].tolist())
        self.outlinePoly = gc.poly.Polygon(self.outlineVerts)
        self.expandedOutlinePoly = self.outlinePoly.growPoly(self.coarseToolCutDiameter/2)

    def EOX(self, ): # exterior offset X
        return self.boxExteriorX / 2

    def EOY(self, ): # exterior offset X
        return self.boxExteriorY / 2

    def addFineCuts(self, asm):
        super().addFineCuts(asm)
        toolCutDiameter = self.fineToolCutDiameter
        HSX = self.workpieceDepth / 2  # half slot X
        # HSY = 3 * self.workpieceDepth / 2  # half slot Y
        HSY = self.tabLength / 2  # half slot Y
        slotVertices = np.asarray(((-HSX, -HSY),
                                   (HSX, -HSY),
                                   (HSX, HSY),
                                   (-HSX, HSY),
                                   ))
        baseSlotYOffset = (1 / 5) * self.boxExteriorY
        baseSlotXOffset = self.interiorX / 2 + self.workpieceDepth / 2
        for slotYOffset in (baseSlotYOffset, -baseSlotYOffset):
            for slotXOffset in (baseSlotXOffset, -baseSlotXOffset):
                offsetArr = np.asarray([np.asarray((slotXOffset, slotYOffset)) for vert in slotVertices])
                offsetSlotVertices = slotVertices + offsetArr
                # slotPoly = gc.poly.Polygon(offsetSlotVertices).shrinkPoly(toolCutDiameter / 2)
                slotPoly = gc.poly.PolygonInsideDogbone(offsetSlotVertices, shrinkAmount=toolCutDiameter / 2)
                asm += gc.cut.PolygonCut(slotPoly, self.cutDepth)


class LeftRightBoxFace(SimpleBoxBaseFace):
    def __init__(self,
                 name,
                 interiorX,
                 interiorY,
                 workpieceDepth,
                 tabLength,
                 postTabThickness,
                 coarseToolCutDiameter,
                 fineToolCutDiameter,
                 workpieceExtraCutDepth=0.8,
                 customFaceCut=None,
                 ):
        super().__init__(name,
                         interiorX,
                         interiorY,
                         workpieceDepth,
                         tabLength,
                         postTabThickness,
                         coarseToolCutDiameter,
                         fineToolCutDiameter,
                         workpieceExtraCutDepth,
                         customFaceCut, )
        self.outlineVerts = self.baseOutlineVerts.copy()
        #
        tabYStops = []
        for tabCenter in (-0.2 * self.boxExteriorY, 0.2 * self.boxExteriorY):
            # for tabOffset in (-3 * self.workpieceDepth / 2, 3 * self.workpieceDepth / 2):
            for tabOffset in (-self.tabLength / 2, self.tabLength / 2):
                tabYStops.append(tabCenter + tabOffset)
        #
        rightTabs = []
        rightTabs.append(np.asarray((self.outlineVerts[1][0], tabYStops[0])))
        rightTabs.append(rightTabs[-1] + np.asarray((self.workpieceDepth, 0)))
        rightTabs.append(np.asarray((rightTabs[-1][0], tabYStops[1])))
        rightTabs.append(rightTabs[-1] + np.asarray((-self.workpieceDepth, 0)))
        rightTabs.append(np.asarray((rightTabs[-1][0], tabYStops[2])))
        rightTabs.append(rightTabs[-1] + np.asarray((self.workpieceDepth, 0)))
        rightTabs.append(np.asarray((rightTabs[-1][0], tabYStops[3])))
        rightTabs.append(rightTabs[-1] + np.asarray((-self.workpieceDepth, 0)))
        #
        leftTabs = []
        leftTabs.append(np.asarray((self.outlineVerts[3][0], tabYStops[3])))
        leftTabs.append(leftTabs[-1] + np.asarray((-self.workpieceDepth, 0)))
        leftTabs.append(np.asarray((leftTabs[-1][0], tabYStops[2])))
        leftTabs.append(leftTabs[-1] + np.asarray((self.workpieceDepth, 0)))
        leftTabs.append(np.asarray((leftTabs[-1][0], tabYStops[1])))
        leftTabs.append(leftTabs[-1] + np.asarray((-self.workpieceDepth, 0)))
        leftTabs.append(np.asarray((leftTabs[-1][0], tabYStops[0])))
        leftTabs.append(leftTabs[-1] + np.asarray((self.workpieceDepth, 0)))
        #
        self.outlineVerts = (np.asarray(self.outlineVerts[0:2].tolist() + rightTabs +
                                        self.outlineVerts[2:].tolist() + leftTabs))
        self.outlinePoly = gc.poly.Polygon(self.outlineVerts)
        self.expandedOutlinePoly = self.outlinePoly.growPoly(self.coarseToolCutDiameter/2)

    def EOX(self, ): # exterior offset X
        return self.interiorX / 2

    def EOY(self, ): # exterior offset X
        return self.boxExteriorY / 2

    def addFineCuts(self, asm):
        super().addFineCuts(asm)
        toolCutDiameter = self.fineToolCutDiameter
        #HSX = 3 * self.workpieceDepth / 2  # half slot X
        HSX = self.tabLength / 2  # half slot X
        HSY = self.workpieceDepth / 2  # half slot Y
        slotVertices = np.asarray(((-HSX, -HSY),
                                   (HSX, -HSY),
                                   (HSX, HSY),
                                   (-HSX, HSY),
                                   ))
        baseSlotYOffset = self.interiorY / 2 + self.workpieceDepth / 2
        baseSlotXOffset = (1 / 5) * self.boxExteriorX
        for slotYOffset in (baseSlotYOffset, -baseSlotYOffset):
            for slotXOffset in (baseSlotXOffset, -baseSlotXOffset):
                offsetArr = np.asarray([np.asarray((slotXOffset, slotYOffset)) for vert in slotVertices])
                offsetSlotVertices = slotVertices + offsetArr
                # slotPoly = gc.poly.Polygon(offsetSlotVertices).shrinkPoly(toolCutDiameter / 2)
                slotPoly = gc.poly.PolygonInsideDogbone(offsetSlotVertices, shrinkAmount=toolCutDiameter / 2)
                asm += gc.cut.PolygonCut(slotPoly, self.cutDepth)
        #
        self.dogboneFineOutlineCleanup(asm)


class TopBottomBoxFace(SimpleBoxBaseFace):
    def __init__(self,
                 name,
                 interiorX,
                 interiorY,
                 workpieceDepth,
                 tabLength,
                 postTabThickness,
                 coarseToolCutDiameter,
                 fineToolCutDiameter,
                 workpieceExtraCutDepth=0.8,
                 customFaceCut=None,
                 ):
        super().__init__(name,
                         interiorX,
                         interiorY,
                         workpieceDepth,
                         tabLength,
                         postTabThickness,
                         coarseToolCutDiameter,
                         fineToolCutDiameter,
                         workpieceExtraCutDepth,
                         customFaceCut, )
        self.outlineVerts = self.baseOutlineVerts.copy()
        #
        tabYStops = []
        for tabCenter in (-0.2 * self.boxExteriorY, 0.2 * self.boxExteriorY):
            # for tabOffset in (-3 * self.workpieceDepth / 2, 3 * self.workpieceDepth / 2):
            for tabOffset in (-self.tabLength / 2, self.tabLength / 2):
                tabYStops.append(tabCenter + tabOffset)
        #
        rightTabs = []
        rightTabs.append(np.asarray((self.outlineVerts[1][0], tabYStops[0])))
        rightTabs.append(rightTabs[-1] + np.asarray((self.workpieceDepth, 0)))
        rightTabs.append(np.asarray((rightTabs[-1][0], tabYStops[1])))
        rightTabs.append(rightTabs[-1] + np.asarray((-self.workpieceDepth, 0)))
        rightTabs.append(np.asarray((rightTabs[-1][0], tabYStops[2])))
        rightTabs.append(rightTabs[-1] + np.asarray((self.workpieceDepth, 0)))
        rightTabs.append(np.asarray((rightTabs[-1][0], tabYStops[3])))
        rightTabs.append(rightTabs[-1] + np.asarray((-self.workpieceDepth, 0)))
        #
        leftTabs = []
        leftTabs.append(np.asarray((self.outlineVerts[3][0], tabYStops[3])))
        leftTabs.append(leftTabs[-1] + np.asarray((-self.workpieceDepth, 0)))
        leftTabs.append(np.asarray((leftTabs[-1][0], tabYStops[2])))
        leftTabs.append(leftTabs[-1] + np.asarray((self.workpieceDepth, 0)))
        leftTabs.append(np.asarray((leftTabs[-1][0], tabYStops[1])))
        leftTabs.append(leftTabs[-1] + np.asarray((-self.workpieceDepth, 0)))
        leftTabs.append(np.asarray((leftTabs[-1][0], tabYStops[0])))
        leftTabs.append(leftTabs[-1] + np.asarray((self.workpieceDepth, 0)))
        #
        self.outlineVerts = (np.asarray(self.outlineVerts[0:2].tolist() + rightTabs +
                                        self.outlineVerts[2:].tolist() + leftTabs))
        # #
        # topTabs = []
        # topTabs.append(self.outlineVerts[2] + np.asarray((-0.2 * self.boxExteriorX, 0)))
        # topTabs.append(topTabs[-1] + np.asarray((0, self.workpieceDepth)))
        # topTabs.append(topTabs[-1] + np.asarray((-0.2 * self.boxExteriorX, 0)))
        # topTabs.append(topTabs[-1] + np.asarray((0, -self.workpieceDepth)))
        # topTabs.append(topTabs[-1] + np.asarray((-0.2 * self.boxExteriorX, 0)))
        # topTabs.append(topTabs[-1] + np.asarray((0, self.workpieceDepth)))
        # topTabs.append(topTabs[-1] + np.asarray((-0.2 * self.boxExteriorX, 0)))
        # topTabs.append(topTabs[-1] + np.asarray((0, -self.workpieceDepth)))
        # #
        # bottomTabs = []
        # bottomTabs.append(self.outlineVerts[0] + np.asarray((0.2 * self.boxExteriorX, 0)))
        # bottomTabs.append(bottomTabs[-1] + np.asarray((0, -self.workpieceDepth)))
        # bottomTabs.append(bottomTabs[-1] + np.asarray((0.2 * self.boxExteriorX, 0)))
        # bottomTabs.append(bottomTabs[-1] + np.asarray((0, self.workpieceDepth)))
        # bottomTabs.append(bottomTabs[-1] + np.asarray((0.2 * self.boxExteriorX, 0)))
        # bottomTabs.append(bottomTabs[-1] + np.asarray((0, -self.workpieceDepth)))
        # bottomTabs.append(bottomTabs[-1] + np.asarray((0.2 * self.boxExteriorX, 0)))
        # bottomTabs.append(bottomTabs[-1] + np.asarray((0, self.workpieceDepth)))
        # #
        # self.outlineVerts = (np.asarray(self.outlineVerts[0:1].tolist() + bottomTabs +
        #                                 self.outlineVerts[1:3].tolist() + topTabs +
        #                                 self.outlineVerts[3:].tolist()))
        self.outlinePoly = gc.poly.Polygon(self.outlineVerts)
        self.expandedOutlinePoly = self.outlinePoly.growPoly(self.coarseToolCutDiameter/2)

    def EOX(self, ): # exterior offset X
        return self.interiorX / 2

    def EOY(self, ): # exterior offset Y
        return self.interiorY / 2

    def addFineCuts(self, asm):
        super().addFineCuts(asm)
        self.dogboneFineOutlineCleanup(asm)

        # for vertIdx in self.expandedOutlinePoly.getInsideCornerIndices():
        #     baseVert = self.outlinePoly.vertices[vertIdx]
        #     expandedVert = self.expandedOutlinePoly.vertices[vertIdx]
        #     cornerVerts = self.expandedOutlinePoly.getCornerVertsForIndex(vertIdx)
        #     # gc.debug.DBGP(cornerVerts)
        #     cornerOrientation = gc.vertex.getOrientation(cornerVerts)
        #     # gc.debug.DBGP(cornerOrientation)
        #     dogbonedInnerVerts = []
        #     dogbonedInnerVerts.append(cornerVerts[0])
        #     dogbonedInnerVerts.append(expandedVert)
        #     # vec0, vec1 = gc.vertex.cornerToVectors(corner)
        #     vec0, vec1 = (cornerVerts[1] - cornerVerts[0], cornerVerts[-1] - cornerVerts[0], )
        #     diagonal = (gc.vertex.toUnitVec(vec0) + gc.vertex.toUnitVec(vec1))
        #     moveDirection = -gc.vertex.toUnitVec(diagonal)
        #     moveAmount = self.fineToolCutDiameter/2
        #     dogbonePoint = baseVert - moveDirection * moveAmount
        #     dogbonedInnerVerts.append(dogbonePoint)
        #     dogbonedInnerVerts.append(expandedVert)
        #     dogbonedInnerVerts.append(cornerVerts[-1])
        #     dogbonedInnerPoly = gc.poly.Polygon(dogbonedInnerVerts)
        #     asm += gc.cut.PolygonCut(dogbonedInnerPoly, depth=self.cutDepth)
        #     dogbonedInnerPoly.plot(figure=True, show=False, color='r')
        #     self.outlinePoly.plot(figure=False, show=False, color='k')
        #     self.expandedOutlinePoly.plot(figure=False, show=True, color='b')


class SimpleBox(gc.hg_coords.Transformable):
    FACE_FRONT, FACE_BACK, FACE_LEFT, FACE_RIGHT, FACE_TOP, FACE_BOTTOM = range(6)
    FACE_DICT = dict(((FACE_FRONT, 'FACE_FRONT'), (FACE_BACK, 'FACE_BACK'),
                      (FACE_LEFT, 'FACE_LEFT'), (FACE_RIGHT, 'FACE_RIGHT'),
                      (FACE_TOP, 'FACE_TOP'), (FACE_BOTTOM, 'FACE_BOTTOM'), ))
    FACES = FACE_DICT.keys()
    def __init__(self,
                 name,
                 interiorWidth,
                 interiorHeight,
                 interiorDepth,
                 workpieceWidth,
                 workpieceHeight,
                 workpieceDepth,
                 tabLength,
                 postTabThickness,
                 footWidth,
                 footDepth,
                 coarseCutTool,
                 fineCutTool,
                 workpieceExtraCutDepth=0.8,
                 customFaceCutDict=None,
                 ):
        initFromDict(locals())
        super().__init__()
        if self.customFaceCutDict is None:
            self.customFaceCutDict = {}
        self.asmCoarse = self.init_mill_Coarse()
        self.asmFine = self.init_mill_Fine()
        #self.faces = [{'o': None, 'Coarse': self.asmCoarse, 'Fine': self.asmFine, } for face in SimpleBox.FACES]
        self.faces = []
        for key in SimpleBox.FACE_DICT.keys():
            faceId = SimpleBox.FACE_DICT[key]
            self.asmFine += gc.assembly.Assembly(name="{}Asm".format(faceId))
            self.asmCoarse += gc.assembly.Assembly(name="{}Asm".format(faceId))
            self.faces.append({'o': None, 'Coarse': self.asmCoarse.last(), 'Fine': self.asmFine.last(), })
            if key not in self.customFaceCutDict:
                self.customFaceCutDict[key] = None
        for faceId in (SimpleBox.FACE_FRONT, SimpleBox.FACE_BACK):
            self.faces[faceId]['o'] = (
                FrontBackBoxFace(name=self.name + '_' + SimpleBox.FACE_DICT[faceId],
                                 interiorX=self.interiorWidth,
                                 interiorY=self.interiorDepth,
                                 workpieceDepth=self.workpieceDepth,
                                 tabLength=self.tabLength,
                                 postTabThickness=self.postTabThickness,
                                 footWidth=self.footWidth,
                                 footDepth=self.footDepth,
                                 coarseToolCutDiameter=self.asmCoarse.cncCfg['tool'].cutDiameter,
                                 fineToolCutDiameter=self.asmFine.cncCfg['tool'].cutDiameter,
                                 customFaceCut=self.customFaceCutDict[faceId],
                                 )
                )
        for faceId in (SimpleBox.FACE_LEFT, SimpleBox.FACE_RIGHT):
            self.faces[faceId]['o'] = (
                LeftRightBoxFace(name=self.name + '_' + SimpleBox.FACE_DICT[faceId],
                                 interiorX=self.interiorHeight,
                                 interiorY=self.interiorDepth,
                                 workpieceDepth=self.workpieceDepth,
                                 tabLength=self.tabLength,
                                 postTabThickness=self.postTabThickness,
                                 coarseToolCutDiameter=self.asmCoarse.cncCfg['tool'].cutDiameter,
                                 fineToolCutDiameter=self.asmFine.cncCfg['tool'].cutDiameter,
                                 customFaceCut=self.customFaceCutDict[faceId],
                                 )
                )
        for faceId in (SimpleBox.FACE_TOP, SimpleBox.FACE_BOTTOM):
            self.faces[faceId]['o'] = (
                TopBottomBoxFace(name=self.name + '_' + SimpleBox.FACE_DICT[faceId],
                                 interiorX=self.interiorWidth,
                                 interiorY=self.interiorHeight,
                                 workpieceDepth=self.workpieceDepth,
                                 tabLength=self.tabLength,
                                 postTabThickness=self.postTabThickness,
                                 coarseToolCutDiameter=self.asmCoarse.cncCfg['tool'].cutDiameter,
                                 fineToolCutDiameter=self.asmFine.cncCfg['tool'].cutDiameter,
                                 customFaceCut=self.customFaceCutDict[faceId],
                                 )
                )

    def translateFace(self, faceId, x=0, y=0, z=0):
        self.faces[faceId]['Coarse'].translate(x, y, z)
        self.faces[faceId]['Fine'].translate(x, y, z)

    def rotateFace(self, faceId, phi=np.pi/2, x=0, y=0, z=1):
        self.faces[faceId]['Coarse'].rotate(phi, x, y, z)
        self.faces[faceId]['Fine'].rotate(phi, x, y, z)

    def moveHelper(self, faceId, x, y, doRot=False):
        # print(SimpleBox.FACE_DICT[faceId], sizeX, sizeY)
        if doRot:
            self.rotateFace(faceId)
            sizeX, sizeY = self.faces[faceId]['rectBounds']
            self.translateFace(faceId, sizeY, 0, )
        # else:
        #     self.translateFace(faceId, -sizeX/2, -sizeY/2, )
        self.translateFace(faceId, x, y)
        self.translateFace(faceId, -(self.workpieceWidth - EDGE_MARGIN)/2, -(self.workpieceHeight - EDGE_MARGIN)/2)

    def gen(self):
        for faceIdx in SimpleBox.FACES:
            self.gen_face(faceIdx)
        #
        rectsToPack = []
        for faceIdx in SimpleBox.FACES:
            width, height = self.faces[faceIdx]['rectBounds']
            rect = rect_pack.Rect(0, 0, width, height, data=faceIdx)
            rectsToPack.append(rect)
        packer = rect_pack.RectPack((self.workpieceWidth - EDGE_MARGIN), (self.workpieceHeight - EDGE_MARGIN))
        packer.pack(rectsToPack)
        for rect in packer.packedRectList:
            self.moveHelper(rect.data, rect.x, rect.y, doRot=rect.rotated)
        #
        # FIXME this should be done elsewhere, and its probably not quite right!
        for faceIdx in SimpleBox.FACES:
            WASTEBOARD_BOT_LEFT = np.asarray((-187.2-12.7, -195.3-12.7))
            print("WASTEBOARD_BOT_LEFT: ", WASTEBOARD_BOT_LEFT)
            WASTEBOARD_TOP_RIGHT = WASTEBOARD_BOT_LEFT + 177.8 + 2 * 12.7
            print("WASTEBOARD_TOP_RIGHT: ", WASTEBOARD_TOP_RIGHT)
            WASTEBOARD_DIMS = WASTEBOARD_TOP_RIGHT - WASTEBOARD_BOT_LEFT
            print("WASTEBOARD_DIMS: ", WASTEBOARD_DIMS)
            WASTEBOARD_CENTER = (WASTEBOARD_BOT_LEFT + WASTEBOARD_TOP_RIGHT) / 2
            print("WASTEBOARD_CENTER: ", WASTEBOARD_CENTER)
            translate = WASTEBOARD_CENTER / 2
            print(translate)
            self.translateFace(faceIdx, *(WASTEBOARD_CENTER))
        #
        if FAST_SCAD:
            self.asmCoarse.cncCfg["defaultDepthPerMillingPass"] = 1000
            self.asmFine.cncCfg["defaultDepthPerMillingPass"] = 1000
        #
        wName = "{}{}".format(self.name, "_CoarseAsm")
        scadName = "{}{}".format(wName, ".scad")
        with open(scadName, 'w') as ofp:
            ofp.write(self.asmCoarse.genScad())
        log.info("wrote {}".format(scadName))
        if not FAST_SCAD:
            gcodeName = "{}{}".format(wName, ".gcode")
            with open(gcodeName, 'w') as ofp:
                ofp.write(self.asmCoarse.genGcode())
            log.info("wrote {}".format(gcodeName))
        #
        wName = "{}{}".format(self.name, "_FineAsm")
        scadName = "{}{}".format(wName, ".scad")
        with open(scadName, 'w') as ofp:
            ofp.write(self.asmFine.genScad())
        log.info("wrote {}".format(scadName))
        if not FAST_SCAD:
            gcodeName = "{}{}".format(wName, ".gcode")
            with open(gcodeName, 'w') as ofp:
                ofp.write(self.asmFine.genGcode())
            log.info("wrote {}".format(gcodeName))
        #
        toolPathMap = {}
        for asm in (self.asmCoarse, self.asmFine):
            toolPathMap[asm.name] = asm.genScadToolPath()
        genScadMainCust = partial(self.genScadMainX,
                                  toolPathMap=toolPathMap)
        wName = "{}{}".format(self.name, "_all")
        scadName = "{}{}".format(wName, ".scad")
        with open(scadName, 'w') as ofp:
            scadAll = gc.scad.genScad(toolMotions=[], cncCfg=None, name="all", main=genScadMainCust)
            ofp.write(str(scadAll))
        log.info("wrote {}".format(scadName))

    def init_mill_Coarse(self):
        comments = []
        comments.append("""box Mill_Coarse""")
        bit = self.coarseCutTool
        comments.append("tool: {}".format(bit))
        cncCfg = gc.machine.CncMachineConfig(bit,
                                             zSafe=40,
                                             zMargin=0.5,
                                             )
        #
        asmFile = gc.assembly.FileAsm(name="boxMill_Coarse", cncCfg=cncCfg, comments=comments, scadMain=self.genScadMain, )
        return asmFile

    def init_mill_Fine(self):
        comments = []
        comments.append("""box Mill_Fine""")
        bit = self.fineCutTool
        comments.append("tool: {}".format(bit))
        cncCfg = gc.machine.CncMachineConfig(bit,
                                             zSafe=40,
                                             zMargin=0.5,
                                             )
        #
        asmFile = gc.assembly.FileAsm(name="boxMill_Fine", cncCfg=cncCfg, comments=comments, scadMain=self.genScadMain)
        return asmFile

    def gen_front_face(self):
        self.gen_face(SimpleBox.FACE_FRONT)

    def gen_left_face(self):
        self.gen_face(SimpleBox.FACE_LEFT)

    def gen_top_face(self):
        self.gen_face(SimpleBox.FACE_TOP)

    def gen_face(self, faceId):
        faceDict = self.faces[faceId]
        faceObj = faceDict["o"]
        faceObj.addFineCuts(faceDict["Fine"])
        faceObj.addCoarseCuts(faceDict["Coarse"])
        botLeft = np.amin(faceObj.expandedOutlinePoly.boundingBox, axis=0)
        topRight = np.amax(faceObj.expandedOutlinePoly.boundingBox, axis=0)
        rectBounds = (topRight-botLeft)
        self.translateFace(faceId, *(-botLeft))
        faceDict['rectBounds'] = rectBounds
        # print(faceId, rectBounds)

    def genScadMain(self, toolPathName):
        result = []
        result.extend(self.getScadWorkPiece())
        result.append("module main () {")
        if SCAD_SHOW_WORKPIECE:
            result.append("  difference() {")
            result.append("    workpiece();")
        result.append("    union() {")
        result.append("      {}();".format(toolPathName))
        if SCAD_SHOW_WORKPIECE:
            result.append("    }")
        result.append("  }")
        result.append("}")
        return result

    # used for _all.scad
    def genScadMainX(self, toolpath, toolPathMap):
        result = []
        result.extend(self.getScadWorkPiece())
        for key, val in toolPathMap.items():
            result.extend(val)
        result.append("")
        result.append("module main () {")
        if SCAD_SHOW_WORKPIECE:
            result.append("    difference() {")
            result.append("      workpiece();")
        # start do tool paths
        result.append("      union() {")
        for key in toolPathMap:
            result.append("        {}();".format(gc.scad.makeToolPathName(key)))
        result.append("      }")
        # end do tool paths
        if SCAD_SHOW_WORKPIECE:
            result.append("    }")
        result.append("}")
        return result

    def getScadWorkPiece(self):
        result = []
        result.append("module workpiece() {")
        # FIXME  this is a mess
        WASTEBOARD_BOT_LEFT = np.asarray((-187.2-12.7, -195.3-12.7))
        #result.append("  translate([{}, {}, {}]) ".format(-self.workpieceWidth/2, -self.workpieceHeight/2, -self.workpieceDepth))
        result.append("  translate([{}, {}, {}]) ".format(WASTEBOARD_BOT_LEFT[0],
                                                          WASTEBOARD_BOT_LEFT[1],
                                                          -self.workpieceDepth, ))
        result.append("  cube([{}, {}, {}]);".format(self.workpieceWidth, self.workpieceHeight, self.workpieceDepth))
        #result.append("  square([{}, {}]);".format(self.workpieceWidth, self.workpieceHeight))
        result.append("}")
        result.append("")
        return result

def ethernetCut(toolCutDiameter):
    ethXs = (12.7345, 29.3315, )
    ethYs = (11.694 + 5, 26.304 + 5, )
    verts = np.asarray(((ethXs[0], ethYs[0]),
                        (ethXs[1], ethYs[0]),
                        (ethXs[1], ethYs[1]),
                        (ethXs[0], ethYs[1]),
                        ))
    boxBotLeft = np.asarray((10.5517, 13.02294, ))
    boxBotLeftTiled = np.asarray([boxBotLeft] * len(verts))
    verts -= boxBotLeftTiled
    ethPolyPerim = gc.poly.PolygonInsideDogbone(verts, shrinkAmount=toolCutDiameter/2, )
    return ethPolyPerim

def usbCut(toolCutDiameter, xTrans, yTrans):
    boxBotLeft = np.asarray((10.5517, 13.02294, ))
    usbXs = np.asarray((31.5805, 48.048, ))
    usbXs -= usbXs[0]
    usbXs += xTrans
    usbYs = np.asarray((16.6127, 34.5768, ))
    usbYs -= usbYs[0]
    usbYs += yTrans
    verts = np.asarray(((usbXs[0], usbYs[0]),
                        (usbXs[1], usbYs[0]),
                        (usbXs[1], usbYs[1]),
                        (usbXs[0], usbYs[1]),
                        ))
    boxBotLeftTiled = np.asarray([boxBotLeft] * len(verts))
    verts -= boxBotLeftTiled
    polyPerim = gc.poly.Polygon(vertices=verts, ).shrinkPoly(toolCutDiameter/2)
    return polyPerim


def usb0Cut(toolCutDiameter):
    return usbCut(toolCutDiameter, 31.5805, 16.6127)


def usb1Cut(toolCutDiameter):
    return usbCut(toolCutDiameter, 50.0186, 16.6127)


def main(argv):
    log.setLevel(logging.INFO)
    logHandler = logging.StreamHandler(sys.stdout)
    log.addHandler(logHandler)
    #
    baseName = "demo_box"
    boxBaseWidth = 58 # INTERIOR left face to right face distance
    boxBaseHeight = 88 # INTERIOR front face to back face distance
    boxBaseDepth = 28  # INTERIOR top face to bottom face distance
    #
    coarseCutTool=gc.tool.Carbide3D_102()
    #fineCutTool=gc.tool.Mill_0p01mm()
    #fineCutTool=gc.tool.Mill_0p5mm()
    #fineCutTool=gc.tool.Carbide3D_112()
    fineCutTool=gc.tool.Carbide3D_112()
    #
    customFaceCutDict = dict([(face, {"Coarse":[], "Fine":[], }, ) for face in SimpleBox.FACES])
    #
    ctd = coarseCutTool.cutDiameter
    bc = customFaceCutDict[SimpleBox.FACE_BACK]["Coarse"]
    bc.append(ethernetCut(ctd))
    bc.append(usb0Cut(ctd))
    bc.append(usb1Cut(ctd))
    #
    box = SimpleBox(name=baseName,
                    interiorWidth=boxBaseWidth,
                    interiorHeight=boxBaseHeight,
                    interiorDepth=boxBaseDepth,
                    workpieceWidth=8 * gc.number.mmPerInch,
                    workpieceHeight=8 * gc.number.mmPerInch,
                    workpieceDepth=0.2 * gc.number.mmPerInch,
                    #workpieceDepth=3,
                    #workpieceDepth=4,
                    #postTabThickness=0.25 * gc.number.mmPerInch,
                    tabLength=12,
                    postTabThickness=3,
                    footWidth=8,
                    footDepth=3,
                    coarseCutTool=coarseCutTool,
                    fineCutTool=fineCutTool,
                    customFaceCutDict=customFaceCutDict,
                    )
    box.gen()

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
