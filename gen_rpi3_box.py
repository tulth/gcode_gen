#!/usr/bin/env python
"""Generates gcode that uses nomad 883 to create a box for a rasperry pi 3"""
import sys
import argparse
import logging
import numpy as np
import gcode_gen as gc
import common
from functools import partial
import itertools

SCAD_SHOW_WORKPIECE = True
# SCAD_SHOW_WORKPIECE = False
SCAD_SHOW_RPI3_CCA = SCAD_SHOW_WORKPIECE

WASTEBOARD_BOT_LEFT = np.asarray((-187.2-12.7, -195.3-12.7))
WORKPIECE_BOT_LEFT = WASTEBOARD_BOT_LEFT + np.asarray((8, 8))
log = logging.getLogger()
# log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stdout)
log.addHandler(logHandler)

# WORKPIECE_THICKNESS = 0.125 * gc.number.mmPerInch
WORKPIECE_THICKNESS = 0.2 * gc.number.mmPerInch
WORKPIECE_SIZE = (7.5 * gc.number.mmPerInch, 6.5 * gc.number.mmPerInch, WORKPIECE_THICKNESS)

DEPTH = WORKPIECE_THICKNESS + 0.4

TENON_WIDTH = 10
TENON_DEPTH = WORKPIECE_THICKNESS

class PolygonPerimeter(gc.assembly.Assembly):
    
    def _elab(self, vertices, ):
        self.vertices = self.transforms.doTransform(vertices)
        for v in self.vertices:
            self += gc.cmd.G1(*v)
        self += gc.cmd.G1(*self.vertices[0])

FOOT_WIDTH = 8
FOOT_HEIGHT = 3

class PolygonInsideDogbone(gc.poly.Polygon):
    
    def __init__(self, vertices, shrinkAmount, zVal=None, name=None):
        basePoly = gc.poly.Polygon(vertices=vertices, name="basePoly")
        shrunkPoly = basePoly.shrinkPoly(shrinkAmount)
        dogboneVertices = []
        for baseVert, corner in zip(basePoly.vertices,
                                gc.vertex.verticesToCornersIter(np.roll(shrunkPoly.vertices, 1, axis=0))):
            insideVert = corner[0][1]
            dogboneVertices.append(insideVert)
            vec0, vec1 = gc.vertex.cornerToVectors(corner)
            diagonal = (gc.vertex.toUnitVec(vec0) + gc.vertex.toUnitVec(vec1))
            moveDirection = -gc.vertex.toUnitVec(diagonal)
            moveAmount = shrinkAmount
            dogbonePoint = baseVert - moveDirection * moveAmount
            dogboneVertices.append(dogbonePoint)
            dogboneVertices.append(insideVert)
        super().__init__(dogboneVertices, zVal, name)

class PolygonCut(gc.assembly.Assembly):
    
    def _elab(self,
              polygon,
              depth,
              overlap=None,
              plungeRate=None,
              zMargin=None):
        self.depth = depth
        if overlap is None:
            overlap = self.cncCfg["defaultMillingOverlap"]
        if plungeRate is None:
            plungeRate = self.cncCfg["defaultDrillingFeedRate"]
        if zMargin is None:
            zMargin = self.cncCfg["zMargin"]
        vertices = self.transforms.doTransform(polygon.vertices)
        self += gc.cmd.G0(x=self.center[0], y=self.center[1])
        zStart = self.center[2] + zMargin
        self += gc.cmd.G0(z=zStart)
        zCutSteps = gc.number.calcZSteps(zMargin, -depth, self.cncCfg["defaultDepthPerMillingPass"])
        for zCutStep in zCutSteps:
            self += PolygonPerimeter(vertices).translate(z=zCutStep)
        self += gc.cmd.G0(z=zStart)
        self += gc.cmd.G0(x=self.center[0], y=self.center[1])
        # already did transforms on verts, before passing to children so don't transform children!
        self.transforms = gc.hg_coords.TransformList()

        
class FrontOutlineCut(gc.assembly.Assembly):
    
    def _elab(self,
              depth,
              overlap=None,
              plungeRate=None,
              zMargin=None):
        L = 5.56313
        R = 72.529
        xSteps = np.asarray((L, L + FOOT_WIDTH, R - FOOT_WIDTH, R))
        ySteps = np.asarray((104.242 + 17, 138.205 + 17, 138.205 + FOOT_HEIGHT + 17))
        vertices = np.asarray(((xSteps[0], ySteps[0]),
                               (xSteps[3], ySteps[0]),
                               (xSteps[3], ySteps[2]),
                               (xSteps[2], ySteps[2]),
                               (xSteps[2], ySteps[1]),
                               (xSteps[1], ySteps[1]),
                               (xSteps[1], ySteps[2]),
                               (xSteps[0], ySteps[2]),
                               ))
        vertices = self.transforms.doTransform(vertices)
        self.poly = gc.poly.Polygon(vertices=vertices, name="frontOutline")
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        self.poly = self.poly.growPoly(toolCutDiameter/2)
        self += PolygonCut(self.poly, depth, overlap, plungeRate, zMargin)
        self.transforms = gc.hg_coords.TransformList() 


class BackOutlineCut(gc.assembly.Assembly):
    
    def _elab(self,
              depth,
              overlap=None,
              plungeRate=None,
              zMargin=None):
        L = 5.54937
        R = 72.5152
        xSteps = np.asarray((L, L + FOOT_WIDTH, R - FOOT_WIDTH, R))
        ySteps = np.asarray((3.02204 - FOOT_HEIGHT + 5, 3.02204 + 5, 36.9852 + 5))
        vertices = np.asarray(((xSteps[0], ySteps[0]),
                               (xSteps[1], ySteps[0]),
                               (xSteps[1], ySteps[1]),
                               (xSteps[2], ySteps[1]),
                               (xSteps[2], ySteps[0]),
                               (xSteps[3], ySteps[0]),
                               (xSteps[3], ySteps[2]),
                               (xSteps[0], ySteps[2]),
                               ))
        vertices = self.transforms.doTransform(vertices)
        self.poly = gc.poly.Polygon(vertices=vertices, name="frontOutline")
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        self.poly = self.poly.growPoly(toolCutDiameter/2)
        self += PolygonCut(self.poly, depth, overlap, plungeRate, zMargin)
        self.transforms = gc.hg_coords.TransformList() 
        
class SlotCut(gc.assembly.Assembly):
    
    def _elab(self,
              vertex0,
              vertex1,
              depth,
              overlap=None,
              plungeRate=None,
              zMargin=None):
        vertices = self.transforms.doTransform(np.asarray((vertex0, vertex1)))
        self.depth = depth
        if overlap is None:
            overlap = self.cncCfg["defaultMillingOverlap"]
        if plungeRate is None:
            plungeRate = self.cncCfg["defaultDrillingFeedRate"]
        if zMargin is None:
            zMargin = self.cncCfg["zMargin"]
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        self += gc.cmd.G0(x=self.center[0], y=self.center[1])
        zStart = self.center[2] + zMargin
        self += gc.cmd.G0(z=zStart)
        zCutSteps = gc.number.calcZSteps(zMargin, -depth, self.cncCfg["defaultDepthPerMillingPass"])
        vertexIter = itertools.cycle(vertices)
        for zCutStep, vert in zip(zCutSteps, vertexIter):
            self += gc.cmd.G1(z=zCutStep)
            self += gc.cmd.G1(vert[0], vert[1], )
        vert = next(vertexIter)
        self += gc.cmd.G1(vert[0], vert[1], )
        self += gc.cmd.G0(z=zStart)
        self += gc.cmd.G0(x=self.center[0], y=self.center[1])
        # already did transforms on verts, before passing to children so don't transform children!
        self.transforms = gc.hg_coords.TransformList() 

    
def rpi3_box_mill_C102():
    comments = []
    comments.append("""rpi3 box Mill_C102""")
    bit = gc.tool.Carbide3D_102()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         zMargin=0.5,
                                         )
    #
    asmFile = gc.assembly.FileAsm(name="boxMill_C102", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    asm += rpi3_box_front_mill_C102()
    asm += rpi3_box_top_mill_C102()
    asm += rpi3_box_bot_mill_C102()
    asm += rpi3_box_back_mill_C102()
    asm += rpi3_box_left_mill_C102()
    asm += rpi3_box_right_mill_C102()
    return asmFile.translate(*WORKPIECE_BOT_LEFT)

class rpi3_box_front_mill_C102(gc.assembly.Assembly):
    
    def _elab(self, ):
        # asm.last().translate(5, 5).translate(-177.2, -185.3)
        # sdcard slot
        sdCut0Y = (129.941 + 131.697) / 2 + 17
        self += SlotCut([32.8152 + 1.4, sdCut0Y], [45.2769 - 1.4, sdCut0Y], depth=DEPTH)
        sdCut1Y = sdCut0Y + 3.175 / 2
        self += SlotCut([35.0725 + 1, sdCut1Y], [43.01 - 1, sdCut1Y], depth=DEPTH)
        # front cut out
        self += FrontOutlineCut(DEPTH)

class rpi3_box_back_mill_C102(gc.assembly.Assembly):
    
    def _elab(self, ):
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        # ethernet cut out
        ethXs = (12.7345, 29.3315, )
        ethYs = (11.694 + 5, 26.304 + 5, )
        ethPolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((ethXs[0], ethYs[0]),
                                 (ethXs[1], ethYs[0]),
                                 (ethXs[1], ethYs[1]),
                                 (ethXs[0], ethYs[1]),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(ethPolyPerim, depth=DEPTH)
        # usb0 cut out
        usb0Xs = (31.5805, 48.048, )
        usb0Ys = (11.6127 + 5, 29.5768 + 5, )
        usb0PolyPerim = gc.poly.Polygon(
            vertices=np.asarray(((usb0Xs[0], usb0Ys[0]),
                                 (usb0Xs[1], usb0Ys[0]),
                                 (usb0Xs[1], usb0Ys[1]),
                                 (usb0Xs[0], usb0Ys[1]),
                                 )),
            ).shrinkPoly(toolCutDiameter/2)
        self += PolygonCut(usb0PolyPerim, depth=DEPTH)
        # usb1 cut out
        usb1Xs = (50.0186, 66.4863, )
        usb1Ys = (11.6127 + 5, 29.5768 + 5, )
        usb1PolyPerim = gc.poly.Polygon(
            vertices=np.asarray(((usb1Xs[0], usb1Ys[0]),
                                 (usb1Xs[1], usb1Ys[0]),
                                 (usb1Xs[1], usb1Ys[1]),
                                 (usb1Xs[0], usb1Ys[1]),
                                 )),
            ).shrinkPoly(toolCutDiameter/2)
        self += PolygonCut(usb1PolyPerim, depth=DEPTH)
        # back outline cut out
        self += BackOutlineCut(DEPTH)
        

class rpi3_box_top_mill_C102(gc.assembly.Assembly):
    
    def _elab(self, ):
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        outlineXs = (5.049609, 20.2631, 20.2631 + TENON_WIDTH, 65.2781, 65.2781 + TENON_WIDTH, 90.5102, )
        outlineYs = (53.266 - TENON_DEPTH, 53.266, 110.2311, 110.2311 + TENON_DEPTH, )
        # air vent cut out
        xCenter = (outlineXs[0] + outlineXs[-1]) / 2
        yCenter = (outlineYs[0] + outlineYs[-1]) / 2
        ventCutLen = 50
        ventXs = (xCenter - ventCutLen / 2, xCenter + ventCutLen / 2)
        for yNum in range(5):
            yOffset = (yNum - 2) * 2.5 * toolCutDiameter
            ventY = yCenter + yOffset
            self += SlotCut([ventXs[0], ventY], [ventXs[1], ventY], depth=DEPTH)

        # outline cut out
        baseOutlinePoly = gc.poly.Polygon(
            vertices=np.asarray(((outlineXs[0], outlineYs[1]),
                                 (outlineXs[1], outlineYs[1]),
                                 (outlineXs[1], outlineYs[0]),
                                 (outlineXs[2], outlineYs[0]),
                                 (outlineXs[2], outlineYs[1]),
                                 (outlineXs[3], outlineYs[1]),
                                 (outlineXs[3], outlineYs[0]),
                                 (outlineXs[4], outlineYs[0]),
                                 (outlineXs[4], outlineYs[1]),
                                 (outlineXs[5], outlineYs[1]),
                                 (outlineXs[5], outlineYs[2]),
                                 (outlineXs[4], outlineYs[2]),
                                 (outlineXs[4], outlineYs[3]),
                                 (outlineXs[3], outlineYs[3]),
                                 (outlineXs[3], outlineYs[2]),
                                 (outlineXs[2], outlineYs[2]),
                                 (outlineXs[2], outlineYs[3]),
                                 (outlineXs[1], outlineYs[3]),
                                 (outlineXs[1], outlineYs[2]),
                                 (outlineXs[0], outlineYs[2]),
                                 )),
            )
        expandedOutlinePoly = baseOutlinePoly.growPoly(toolCutDiameter/2)
        dogbonedInnerVerts = []
        if expandedOutlinePoly.isClockwise:
            expectedOrientation = 1
        else:
            expectedOrientation = -1
        # gc.debug.DBGP(expectedOrientation)
        for baseVert, expandedVert, corner in zip(baseOutlinePoly.vertices,
                                                  expandedOutlinePoly.vertices,
                                                  gc.vertex.verticesToCornersIter(np.roll(expandedOutlinePoly.vertices, 1, axis=0))):
            dogbonedInnerVerts.append(expandedVert)
            cornerVerts = np.asarray((corner[0][0], corner[0][1], corner[1][1], ))
            # gc.debug.DBGP(corner)
            # gc.debug.DBGP(cornerVerts)
            cornerOrientation = gc.vertex.getOrientation(cornerVerts)
            # gc.debug.DBGP(cornerOrientation)
            needDogBone = ((cornerOrientation == 0) or
                           (cornerOrientation != expectedOrientation))
            # gc.debug.DBGP(needDogBone)
            if needDogBone:
                vec0, vec1 = gc.vertex.cornerToVectors(corner)
                # diagonal = (gc.vertex.toUnitVec(vec0) + gc.vertex.toUnitVec(vec1))
                diagonal = vec0 + vec1
                moveDirection = -gc.vertex.toUnitVec(diagonal)
                moveAmount = toolCutDiameter/2
                dogbonePoint = baseVert - moveDirection * moveAmount
                dogbonedInnerVerts.append(dogbonePoint)
                dogbonedInnerVerts.append(expandedVert)
                
        dogbonedInnerPoly = gc.poly.Polygon(dogbonedInnerVerts)
        self += PolygonCut(dogbonedInnerPoly, depth=DEPTH)
        

class rpi3_box_left_mill_C102(gc.assembly.Assembly):
    
    def _elab(self, ):
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        outlineXs = (85.5747 - TENON_DEPTH, 85.5747, 171.044, 171.044 + TENON_DEPTH, )
        outlineYs = (121.225, 123.236, 123.236 + TENON_WIDTH, 143.194, 143.194 + TENON_WIDTH, 155.188, )
        # outline cut out
        outlinePoly = gc.poly.Polygon(
            vertices=np.asarray(((outlineXs[0], outlineYs[1]),
                                 (outlineXs[1], outlineYs[1]),
                                 (outlineXs[1], outlineYs[0]),
                                 (outlineXs[2], outlineYs[0]),
                                 (outlineXs[2], outlineYs[1]),
                                 (outlineXs[3], outlineYs[1]),
                                 (outlineXs[3], outlineYs[2]),
                                 (outlineXs[2], outlineYs[2]),
                                 (outlineXs[2], outlineYs[3]),
                                 (outlineXs[3], outlineYs[3]),
                                 (outlineXs[3], outlineYs[4]),
                                 (outlineXs[2], outlineYs[4]),
                                 (outlineXs[2], outlineYs[5]),
                                 (outlineXs[1], outlineYs[5]),
                                 (outlineXs[1], outlineYs[4]),
                                 (outlineXs[0], outlineYs[4]),
                                 (outlineXs[0], outlineYs[3]),
                                 (outlineXs[1], outlineYs[3]),
                                 (outlineXs[1], outlineYs[2]),
                                 (outlineXs[0], outlineYs[2]),
                                 ### Add the clip outline
                                 #(outlineXs[0], outlineYs[1] + 2.5),
                                 #(outlineXs[0] - 3, outlineYs[1] + 2.5),
                                 #(outlineXs[0] - 3, outlineYs[0]),
                                 # (outlineXs[0] - 3, outlineYs[1]-3),
                                 # (outlineXs[0] - 1, outlineYs[1]-3),
                                 #(outlineXs[0] - 2, outlineYs[1] + 2),
                                 )),
            ).growPoly(toolCutDiameter/2)
        self += PolygonCut(outlinePoly, depth=DEPTH)
        

class rpi3_box_right_mill_C102(gc.assembly.Assembly):
    
    def _elab(self, ):
        rightYOffset = -121.225 + 8.02341
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        outlineXs = (85.5747 - TENON_DEPTH, 85.5747, 171.044, 171.044 + TENON_DEPTH, )
        outlineYs = (121.225, 123.236, 123.236 + TENON_WIDTH, 143.194, 143.194 + TENON_WIDTH, 155.188, )
        outlineYs = [outlineY + rightYOffset for outlineY in outlineYs]
        # power cut out
        powerXs = (90.2892, 102.2215, )
        powerYs = (14.3817, 23.3251)
        powerPolyPerim = gc.poly.Polygon(
            vertices=np.asarray(((powerXs[0], powerYs[0]),
                                 (powerXs[1], powerYs[0]),
                                 (powerXs[1], powerYs[1]),
                                 (powerXs[0], powerYs[1]),
                                 )),
            ).shrinkPoly(toolCutDiameter/2)
        self += PolygonCut(powerPolyPerim, depth=DEPTH)
        # hdmi cut out
        hdmiXs = (109.586-1, 112.109, 123.279, 125.805+1, )
        hdmiYs = (17.8213, 19.8139, 24.3477)
        hdmiPolyPerim = gc.poly.Polygon(
            vertices=np.asarray(((hdmiXs[0], hdmiYs[1]),
                                 (hdmiXs[1], hdmiYs[0]),
                                 (hdmiXs[2], hdmiYs[0]),
                                 (hdmiXs[3], hdmiYs[1]),
                                 (hdmiXs[3], hdmiYs[2]),
                                 (hdmiXs[0], hdmiYs[2]),
                                 )),
            ).shrinkPoly(toolCutDiameter/2)
        self += PolygonCut(hdmiPolyPerim, depth=DEPTH)
        # composite av cut out
        centerX = (133.513 + 145.437) / 2
        centerY = (26.332 + 14.40788) / 2
        diameter = 11.924
        avVerts = gc.shape.poly_circle_verts(32) * diameter / 2
        avPoly = gc.poly.Polygon(avVerts).shrinkPoly(toolCutDiameter/2)
        self += PolygonCut(avPoly, depth=DEPTH).translate(centerX, centerY)
        #self += gc.cut.Cylinder(depth=DEPTH,
        #                        diameter=diameter).translate(centerX, centerY)
        # outline cut out
        outlinePoly = gc.poly.Polygon(
            vertices=np.asarray(((outlineXs[0], outlineYs[1]),
                                 (outlineXs[1], outlineYs[1]),
                                 (outlineXs[1], outlineYs[0]),
                                 (outlineXs[2], outlineYs[0]),
                                 (outlineXs[2], outlineYs[1]),
                                 (outlineXs[3], outlineYs[1]),
                                 (outlineXs[3], outlineYs[2]),
                                 (outlineXs[2], outlineYs[2]),
                                 (outlineXs[2], outlineYs[3]),
                                 (outlineXs[3], outlineYs[3]),
                                 (outlineXs[3], outlineYs[4]),
                                 (outlineXs[2], outlineYs[4]),
                                 (outlineXs[2], outlineYs[5]),
                                 (outlineXs[1], outlineYs[5]),
                                 (outlineXs[1], outlineYs[4]),
                                 (outlineXs[0], outlineYs[4]),
                                 (outlineXs[0], outlineYs[3]),
                                 (outlineXs[1], outlineYs[3]),
                                 (outlineXs[1], outlineYs[2]),
                                 (outlineXs[0], outlineYs[2]),
                                 ### Add the clip outline
                                 #(outlineXs[0], outlineYs[1] + 2.5),
                                 #(outlineXs[0] - 3, outlineYs[1] + 2.5),
                                 #(outlineXs[0] - 3, outlineYs[0]),
                                 # (outlineXs[0] - 3, outlineYs[1]-3),
                                 # (outlineXs[0] - 1, outlineYs[1]-3),
                                 #(outlineXs[0] - 2, outlineYs[1] + 2),
                                 )),
            ).growPoly(toolCutDiameter/2)
        self += PolygonCut(outlinePoly, depth=DEPTH)
        

class rpi3_box_left_mill_C112(gc.assembly.Assembly):
    
    def _elab(self, ):
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        outlineXs = (85.5747 - TENON_DEPTH, 85.5747, 171.044, 171.044 + TENON_DEPTH, )
        outlineYs = (121.225, 123.236, 123.236 + TENON_WIDTH, 143.194, 143.194 + TENON_WIDTH, 155.188, )
        # cut assembly mortises (slots)
        # 0    2
        # 1    3
        slot01X0 = 100.7967
        slot01X1 = slot01X0 + TENON_WIDTH
        slot23X0 = 145.82
        slot23X1 = slot23X0 + TENON_WIDTH
        #
        slot13YCenter = (126.225 + 123.226) / 2
        slot13Y0 = slot13YCenter - (WORKPIECE_THICKNESS / 2)
        slot13Y1 = slot13YCenter + (WORKPIECE_THICKNESS / 2)
        slot02YCenter = (150.187 + 153.186) / 2
        slot02Y0 = slot02YCenter - (WORKPIECE_THICKNESS / 2)
        slot02Y1 = slot02YCenter + (WORKPIECE_THICKNESS / 2)
        #slot23X0 = 106.243
        #slot23X1 = slot13Y0 + TENON_WIDTH
        # slot0
        slot0PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot01X0, slot02Y0),
                                 (slot01X1, slot02Y0),
                                 (slot01X1, slot02Y1),
                                 (slot01X0, slot02Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot0PolyPerim, depth=DEPTH)
        # slot1
        slot1PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot01X0, slot13Y0),
                                 (slot01X1, slot13Y0),
                                 (slot01X1, slot13Y1),
                                 (slot01X0, slot13Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot1PolyPerim, depth=DEPTH)
        # slot2
        slot0PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot23X0, slot02Y0),
                                 (slot23X1, slot02Y0),
                                 (slot23X1, slot02Y1),
                                 (slot23X0, slot02Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot0PolyPerim, depth=DEPTH)
        # slot3
        slot1PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot23X0, slot13Y0),
                                 (slot23X1, slot13Y0),
                                 (slot23X1, slot13Y1),
                                 (slot23X0, slot13Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot1PolyPerim, depth=DEPTH)
        
        # outline cut out
        baseOutlinePoly = gc.poly.Polygon(
            vertices=np.asarray(((outlineXs[0], outlineYs[1]),
                                 (outlineXs[1], outlineYs[1]),
                                 (outlineXs[1], outlineYs[0]),
                                 (outlineXs[2], outlineYs[0]),
                                 (outlineXs[2], outlineYs[1]),
                                 (outlineXs[3], outlineYs[1]),
                                 (outlineXs[3], outlineYs[2]),
                                 (outlineXs[2], outlineYs[2]),
                                 (outlineXs[2], outlineYs[3]),
                                 (outlineXs[3], outlineYs[3]),
                                 (outlineXs[3], outlineYs[4]),
                                 (outlineXs[2], outlineYs[4]),
                                 (outlineXs[2], outlineYs[5]),
                                 (outlineXs[1], outlineYs[5]),
                                 (outlineXs[1], outlineYs[4]),
                                 (outlineXs[0], outlineYs[4]),
                                 (outlineXs[0], outlineYs[3]),
                                 (outlineXs[1], outlineYs[3]),
                                 (outlineXs[1], outlineYs[2]),
                                 (outlineXs[0], outlineYs[2]),

                # (outlineXs[0], outlineYs[1]),
                #                  (outlineXs[1], outlineYs[1]),
                #                  (outlineXs[1], outlineYs[0]),
                #                  (outlineXs[2], outlineYs[0]),
                #                  (outlineXs[2], outlineYs[1]),
                #                  (outlineXs[3], outlineYs[1]),
                #                  (outlineXs[3], outlineYs[2]),
                #                  (outlineXs[2], outlineYs[2]),
                #                  (outlineXs[2], outlineYs[3]),
                #                  (outlineXs[3], outlineYs[3]),
                #                  (outlineXs[3], outlineYs[4]),
                #                  (outlineXs[2], outlineYs[4]),
                #                  (outlineXs[2], outlineYs[5]),
                #                  (outlineXs[1], outlineYs[5]),
                #                  (outlineXs[1], outlineYs[4]),
                #                  (outlineXs[0], outlineYs[4]),
                #                  (outlineXs[0], outlineYs[3]),
                #                  (outlineXs[1], outlineYs[3]),
                #                  (outlineXs[1], outlineYs[2]),
                #                  (outlineXs[0], outlineYs[2]),
                                 )),
            )
        expandedOutlinePoly = baseOutlinePoly.growPoly(toolCutDiameter/2)
        if expandedOutlinePoly.isClockwise:
            expectedOrientation = 1
        else:
            expectedOrientation = -1
        # gc.debug.DBGP(expectedOrientation)
        for baseVert, expandedVert, corner in zip(baseOutlinePoly.vertices,
                                                  expandedOutlinePoly.vertices,
                                                  gc.vertex.verticesToCornersIter(np.roll(expandedOutlinePoly.vertices, 1, axis=0))):
            cornerVerts = np.asarray((corner[0][0], corner[0][1], corner[1][1], ))
            # gc.debug.DBGP(corner)
            # gc.debug.DBGP(cornerVerts)
            cornerOrientation = gc.vertex.getOrientation(cornerVerts)
            # gc.debug.DBGP(cornerOrientation)
            needDogBone = ((cornerOrientation == 0) or
                           (cornerOrientation != expectedOrientation))
            # gc.debug.DBGP(needDogBone)
            if needDogBone:
                vec0, vec1 = gc.vertex.cornerToVectors(corner)
                diagonal = (gc.vertex.toUnitVec(vec0) + gc.vertex.toUnitVec(vec1))
                # diagonal = vec0 + vec1
                moveDirection = -gc.vertex.toUnitVec(diagonal)
                moveAmount = toolCutDiameter/2
                dogbonePoint = baseVert - moveDirection * moveAmount
                #dogboneCleanupVerts = (corner[0][0], corner[0][1], dogbonePoint, corner[0][1], corner[1][1], )
                dogboneCleanupVerts = (corner[0][1] + gc.vertex.toUnitVec(vec0),
                                       corner[0][1], dogbonePoint, corner[0][1],
                                       corner[0][1] + gc.vertex.toUnitVec(vec1))
                #dogboneCleanupVerts = (corner[0][1], dogbonePoint, corner[0][1], )
                dogbonedInnerPoly = gc.poly.Polygon(dogboneCleanupVerts)
                self += PolygonCut(dogbonedInnerPoly, depth=DEPTH)
                
        # dogbonedInnerPoly = gc.poly.Polygon(dogbonedInnerVerts)
        # frontTabPoly = gc.poly.Polygon(
        #     vertices=np.asarray(((outlineXs[0], outlineYs[1]),
        #                          (outlineXs[0], outlineYs[1]-1.5),
        #                          (outlineXs[0]-2, outlineYs[1]-1),
        #                          (outlineXs[0], outlineYs[1]+1.5),
        #                          (outlineXs[0], outlineYs[1]+5),
        #                          (outlineXs[0]-5, outlineYs[1]+5),
        #                          (outlineXs[0]-5, outlineYs[1]-5),
        #                          (outlineXs[0]+5, outlineYs[1]-5),
        #                          )),
        #     ).shrinkPoly(toolCutDiameter/2)
        # self += PolygonCut(frontTabPoly, depth=DEPTH)
        # self += SlotCut((outlineXs[0], outlineYs[1] + 2.5),
        #                 (outlineXs[0]+8, outlineYs[1] + 2),
        #                 depth=DEPTH)
        
class rpi3_box_right_mill_C112(gc.assembly.Assembly):
    
    def _elab(self, ):
        rightYOffset = -121.225 + 8.02341
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        outlineXs = (85.5747 - TENON_DEPTH, 85.5747, 171.044, 171.044 + TENON_DEPTH, )
        outlineYs = (121.225, 123.236, 123.236 + TENON_WIDTH, 143.194, 143.194 + TENON_WIDTH, 155.188, )
        outlineYs = [outlineY + rightYOffset for outlineY in outlineYs]
        # cut assembly mortises (slots)
        # 0    2
        # 1    3
        slot01X0 = 100.7967
        slot01X1 = slot01X0 + TENON_WIDTH
        slot23X0 = 145.82
        slot23X1 = slot23X0 + TENON_WIDTH
        #
        slot13YCenter = (126.225 + 123.226) / 2 + rightYOffset
        slot13Y0 = slot13YCenter - (WORKPIECE_THICKNESS / 2)
        slot13Y1 = slot13YCenter + (WORKPIECE_THICKNESS / 2)
        slot02YCenter = (150.187 + 153.186) / 2 + rightYOffset
        slot02Y0 = slot02YCenter - (WORKPIECE_THICKNESS / 2)
        slot02Y1 = slot02YCenter + (WORKPIECE_THICKNESS / 2)
        #slot23X0 = 106.243
        #slot23X1 = slot13Y0 + TENON_WIDTH
        # slot0
        slot0PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot01X0, slot02Y0),
                                 (slot01X1, slot02Y0),
                                 (slot01X1, slot02Y1),
                                 (slot01X0, slot02Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot0PolyPerim, depth=DEPTH)
        # slot1
        slot1PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot01X0, slot13Y0),
                                 (slot01X1, slot13Y0),
                                 (slot01X1, slot13Y1),
                                 (slot01X0, slot13Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot1PolyPerim, depth=DEPTH)
        # slot2
        slot0PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot23X0, slot02Y0),
                                 (slot23X1, slot02Y0),
                                 (slot23X1, slot02Y1),
                                 (slot23X0, slot02Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot0PolyPerim, depth=DEPTH)
        # slot3
        slot1PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot23X0, slot13Y0),
                                 (slot23X1, slot13Y0),
                                 (slot23X1, slot13Y1),
                                 (slot23X0, slot13Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot1PolyPerim, depth=DEPTH)
        
        # outline cut out
        baseOutlinePoly = gc.poly.Polygon(
            vertices=np.asarray(((outlineXs[0], outlineYs[1]),
                                 (outlineXs[1], outlineYs[1]),
                                 (outlineXs[1], outlineYs[0]),
                                 (outlineXs[2], outlineYs[0]),
                                 (outlineXs[2], outlineYs[1]),
                                 (outlineXs[3], outlineYs[1]),
                                 (outlineXs[3], outlineYs[2]),
                                 (outlineXs[2], outlineYs[2]),
                                 (outlineXs[2], outlineYs[3]),
                                 (outlineXs[3], outlineYs[3]),
                                 (outlineXs[3], outlineYs[4]),
                                 (outlineXs[2], outlineYs[4]),
                                 (outlineXs[2], outlineYs[5]),
                                 (outlineXs[1], outlineYs[5]),
                                 (outlineXs[1], outlineYs[4]),
                                 (outlineXs[0], outlineYs[4]),
                                 (outlineXs[0], outlineYs[3]),
                                 (outlineXs[1], outlineYs[3]),
                                 (outlineXs[1], outlineYs[2]),
                                 (outlineXs[0], outlineYs[2]),

                # (outlineXs[0], outlineYs[1]),
                #                  (outlineXs[1], outlineYs[1]),
                #                  (outlineXs[1], outlineYs[0]),
                #                  (outlineXs[2], outlineYs[0]),
                #                  (outlineXs[2], outlineYs[1]),
                #                  (outlineXs[3], outlineYs[1]),
                #                  (outlineXs[3], outlineYs[2]),
                #                  (outlineXs[2], outlineYs[2]),
                #                  (outlineXs[2], outlineYs[3]),
                #                  (outlineXs[3], outlineYs[3]),
                #                  (outlineXs[3], outlineYs[4]),
                #                  (outlineXs[2], outlineYs[4]),
                #                  (outlineXs[2], outlineYs[5]),
                #                  (outlineXs[1], outlineYs[5]),
                #                  (outlineXs[1], outlineYs[4]),
                #                  (outlineXs[0], outlineYs[4]),
                #                  (outlineXs[0], outlineYs[3]),
                #                  (outlineXs[1], outlineYs[3]),
                #                  (outlineXs[1], outlineYs[2]),
                #                  (outlineXs[0], outlineYs[2]),
                                 )),
            )
        expandedOutlinePoly = baseOutlinePoly.growPoly(toolCutDiameter/2)
        if expandedOutlinePoly.isClockwise:
            expectedOrientation = 1
        else:
            expectedOrientation = -1
        # gc.debug.DBGP(expectedOrientation)
        for baseVert, expandedVert, corner in zip(baseOutlinePoly.vertices,
                                                  expandedOutlinePoly.vertices,
                                                  gc.vertex.verticesToCornersIter(np.roll(expandedOutlinePoly.vertices, 1, axis=0))):
            cornerVerts = np.asarray((corner[0][0], corner[0][1], corner[1][1], ))
            # gc.debug.DBGP(corner)
            # gc.debug.DBGP(cornerVerts)
            cornerOrientation = gc.vertex.getOrientation(cornerVerts)
            # gc.debug.DBGP(cornerOrientation)
            needDogBone = ((cornerOrientation == 0) or
                           (cornerOrientation != expectedOrientation))
            # gc.debug.DBGP(needDogBone)
            if needDogBone:
                vec0, vec1 = gc.vertex.cornerToVectors(corner)
                diagonal = (gc.vertex.toUnitVec(vec0) + gc.vertex.toUnitVec(vec1))
                # diagonal = vec0 + vec1
                moveDirection = -gc.vertex.toUnitVec(diagonal)
                moveAmount = toolCutDiameter/2
                dogbonePoint = baseVert - moveDirection * moveAmount
                #dogboneCleanupVerts = (corner[0][0], corner[0][1], dogbonePoint, corner[0][1], corner[1][1], )
                dogboneCleanupVerts = (corner[0][1] + gc.vertex.toUnitVec(vec0),
                                       corner[0][1], dogbonePoint, corner[0][1],
                                       corner[0][1] + gc.vertex.toUnitVec(vec1))
                #dogboneCleanupVerts = (corner[0][1], dogbonePoint, corner[0][1], )
                dogbonedInnerPoly = gc.poly.Polygon(dogboneCleanupVerts)
                self += PolygonCut(dogbonedInnerPoly, depth=DEPTH)
                
        # dogbonedInnerPoly = gc.poly.Polygon(dogbonedInnerVerts)
        # frontTabPoly = gc.poly.Polygon(
        #     vertices=np.asarray(((outlineXs[0], outlineYs[1]),
        #                          (outlineXs[0], outlineYs[1]-1.5),
        #                          (outlineXs[0]-2, outlineYs[1]-1),
        #                          (outlineXs[0], outlineYs[1]+1.5),
        #                          (outlineXs[0], outlineYs[1]+5),
        #                          (outlineXs[0]-5, outlineYs[1]+5),
        #                          (outlineXs[0]-5, outlineYs[1]-5),
        #                          (outlineXs[0]+5, outlineYs[1]-5),
        #                          )),
        #     ).shrinkPoly(toolCutDiameter/2)
        # self += PolygonCut(frontTabPoly, depth=DEPTH)
        # self += SlotCut((outlineXs[0], outlineYs[1] + 2.5),
        #                 (outlineXs[0]+8, outlineYs[1] + 2),
        #                 depth=DEPTH)
        
class rpi3_box_bot_mill_C102(gc.assembly.Assembly):
    
    def _elab(self, ):
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        outlineXs = (5.049609, 20.2631, 20.2631 + TENON_WIDTH, 65.2781, 65.2781 + TENON_WIDTH, 90.5102, )
        # just use top values and offset
        outlineXs = [outlineX - outlineXs[0] + 98.7686 for outlineX in outlineXs]
        outlineYs = (53.266 - TENON_DEPTH, 53.266, 110.2311, 110.2311 + TENON_DEPTH, )
        # outline cut out
        baseOutlinePoly = gc.poly.Polygon(
            vertices=np.asarray(((outlineXs[0], outlineYs[1]),
                                 (outlineXs[1], outlineYs[1]),
                                 (outlineXs[1], outlineYs[0]),
                                 (outlineXs[2], outlineYs[0]),
                                 (outlineXs[2], outlineYs[1]),
                                 (outlineXs[3], outlineYs[1]),
                                 (outlineXs[3], outlineYs[0]),
                                 (outlineXs[4], outlineYs[0]),
                                 (outlineXs[4], outlineYs[1]),
                                 (outlineXs[5], outlineYs[1]),
                                 (outlineXs[5], outlineYs[2]),
                                 (outlineXs[4], outlineYs[2]),
                                 (outlineXs[4], outlineYs[3]),
                                 (outlineXs[3], outlineYs[3]),
                                 (outlineXs[3], outlineYs[2]),
                                 (outlineXs[2], outlineYs[2]),
                                 (outlineXs[2], outlineYs[3]),
                                 (outlineXs[1], outlineYs[3]),
                                 (outlineXs[1], outlineYs[2]),
                                 (outlineXs[0], outlineYs[2]),
                                 )),
            )
        expandedOutlinePoly = baseOutlinePoly.growPoly(toolCutDiameter/2)
        dogbonedInnerVerts = []
        if expandedOutlinePoly.isClockwise:
            expectedOrientation = 1
        else:
            expectedOrientation = -1
        # gc.debug.DBGP(expectedOrientation)
        for baseVert, expandedVert, corner in zip(baseOutlinePoly.vertices,
                                                  expandedOutlinePoly.vertices,
                                                  gc.vertex.verticesToCornersIter(np.roll(expandedOutlinePoly.vertices, 1, axis=0))):
            dogbonedInnerVerts.append(expandedVert)
            cornerVerts = np.asarray((corner[0][0], corner[0][1], corner[1][1], ))
            # gc.debug.DBGP(corner)
            # gc.debug.DBGP(cornerVerts)
            cornerOrientation = gc.vertex.getOrientation(cornerVerts)
            # gc.debug.DBGP(cornerOrientation)
            needDogBone = ((cornerOrientation == 0) or
                           (cornerOrientation != expectedOrientation))
            # gc.debug.DBGP(needDogBone)
            if needDogBone:
                vec0, vec1 = gc.vertex.cornerToVectors(corner)
                # diagonal = (gc.vertex.toUnitVec(vec0) + gc.vertex.toUnitVec(vec1))
                diagonal = vec0 + vec1
                moveDirection = -gc.vertex.toUnitVec(diagonal)
                moveAmount = toolCutDiameter/2
                dogbonePoint = baseVert - moveDirection * moveAmount
                dogbonedInnerVerts.append(dogbonePoint)
                dogbonedInnerVerts.append(expandedVert)
                
        dogbonedInnerPoly = gc.poly.Polygon(dogbonedInnerVerts)
        self += PolygonCut(dogbonedInnerPoly, depth=DEPTH)
        


class rpi3_box_front_mill_C112(gc.assembly.Assembly):
    
    def _elab(self, ):
        # cut assembly mortises (slots)
        # 0    2
        # 1    3
        slot01XCenter = (7.55992 + 10.5599) / 2
        slot01X0 = slot01XCenter - (WORKPIECE_THICKNESS / 2)
        slot01X1 = slot01XCenter + (WORKPIECE_THICKNESS / 2)
        slot23XCenter = (67.5266 + 70.5266) / 2
        slot23X0 = slot23XCenter - (WORKPIECE_THICKNESS / 2)
        slot23X1 = slot23XCenter + (WORKPIECE_THICKNESS / 2)
        #slot23X0 = 106.243
        #slot23X1 = slot13Y0 + TENON_WIDTH
        slot02Y0 = 126.2 + 17
        slot02Y1 = slot02Y0 + TENON_WIDTH
        slot13Y0 = 106.243 + 17
        slot13Y1 = slot13Y0 + TENON_WIDTH
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        # slot0
        slot0PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot01X0, slot02Y0),
                                 (slot01X1, slot02Y0),
                                 (slot01X1, slot02Y1),
                                 (slot01X0, slot02Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot0PolyPerim, depth=DEPTH)
        # slot1
        slot1PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot01X0, slot13Y0),
                                 (slot01X1, slot13Y0),
                                 (slot01X1, slot13Y1),
                                 (slot01X0, slot13Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot1PolyPerim, depth=DEPTH)
        # slot2
        slot0PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot23X0, slot02Y0),
                                 (slot23X1, slot02Y0),
                                 (slot23X1, slot02Y1),
                                 (slot23X0, slot02Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot0PolyPerim, depth=DEPTH)
        # slot3
        slot1PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot23X0, slot13Y0),
                                 (slot23X1, slot13Y0),
                                 (slot23X1, slot13Y1),
                                 (slot23X0, slot13Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot1PolyPerim, depth=DEPTH)
        

class rpi3_box_back_mill_C112(gc.assembly.Assembly):
    
    def _elab(self, ):
        # cut assembly mortises (slots)
        # 0    2
        # 1    3
        slot01XCenter = (7.55167 + 10.5517) / 2
        slot01X0 = slot01XCenter - (WORKPIECE_THICKNESS / 2)
        slot01X1 = slot01XCenter + (WORKPIECE_THICKNESS / 2)
        slot23XCenter = (67.5171 + 70.5171) / 2
        slot23X0 = slot23XCenter - (WORKPIECE_THICKNESS / 2)
        slot23X1 = slot23XCenter + (WORKPIECE_THICKNESS / 2)
        #slot23X0 = 106.243
        #slot23X1 = slot13Y0 + TENON_WIDTH
        slot02Y0 = 24.9825  + 5
        slot02Y1 = slot02Y0 + TENON_WIDTH
        slot13Y0 = 5.02571 + 5
        slot13Y1 = slot13Y0 + TENON_WIDTH
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        # slot0
        slot0PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot01X0, slot02Y0),
                                 (slot01X1, slot02Y0),
                                 (slot01X1, slot02Y1),
                                 (slot01X0, slot02Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot0PolyPerim, depth=DEPTH)
        # slot1
        slot1PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot01X0, slot13Y0),
                                 (slot01X1, slot13Y0),
                                 (slot01X1, slot13Y1),
                                 (slot01X0, slot13Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot1PolyPerim, depth=DEPTH)
        # slot2
        slot0PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot23X0, slot02Y0),
                                 (slot23X1, slot02Y0),
                                 (slot23X1, slot02Y1),
                                 (slot23X0, slot02Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot0PolyPerim, depth=DEPTH)
        # slot3
        slot1PolyPerim = PolygonInsideDogbone(
            vertices=np.asarray(((slot23X0, slot13Y0),
                                 (slot23X1, slot13Y0),
                                 (slot23X1, slot13Y1),
                                 (slot23X0, slot13Y1),
                                 )),
                                 shrinkAmount=toolCutDiameter/2, 
            )
        self += PolygonCut(slot1PolyPerim, depth=DEPTH)
        

def rpi3_box_mill_C112():
    comments = []
    comments.append("""rpi3 box Mill_C112""")
    bit = gc.tool.Carbide3D_112()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         zMargin=0.5,
                                         )
    #
    asmFile = gc.assembly.FileAsm(name="boxMill_C112", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    asm += rpi3_box_front_mill_C112()
    asm += rpi3_box_back_mill_C112()
    asm += rpi3_box_left_mill_C112()
    asm += rpi3_box_right_mill_C112()
    return asmFile.translate(*WORKPIECE_BOT_LEFT)


def getScadWorkPiece(workpieceThickness):
    result = []
    result.append("module workpiece() {")
    result.append("  translate([{}, {}, {}]) ".format(*WORKPIECE_BOT_LEFT, -workpieceThickness))
    #result.append("  translate([{}, {}, {}]) ".format(*common.botLeft, -workpieceThickness))
    result.append("  cube([{}, {}, {}]);".format(WORKPIECE_SIZE[0], WORKPIECE_SIZE[1], workpieceThickness))
    result.append("}")
    result.append("")
    return result
    

def getDxfExample():
    result = []
    result.append("module dxf () {")
    result.append("  translate([0,0,1])")
    result.append("  translate([{}, {}, {}]) ".format(*WORKPIECE_BOT_LEFT, 0))
    #result.append("  translate([5,5,0])")
    #result.append("  translate([-177.2, -185.3, 0]) ")
    result.append('  import("/home/tulth/projects/rpi3_case/lasercut_example/raspberrypi-b-plus-case_spaced_out.dxf");')
    result.append("}")
    result.append("")
    return result
    

# used for scad layers EXCEPT FOR _all.scad
def genScadMain(toolPathName):
    result = []
    result.extend(getScadWorkPiece(workpieceThickness=WORKPIECE_THICKNESS))  # FIXME
    result.extend(getDxfExample())
    result.append("module main () {")
    result.append("  union() {")
    result.append("  % dxf(); ")

    if SCAD_SHOW_WORKPIECE:
        result.append("  difference() {")
        result.append("    workpiece();")
    result.append("    union() {")
    result.append("      {}();".format(toolPathName))
    if SCAD_SHOW_WORKPIECE:
        result.append("    }")
    result.append("  }")
    result.append("}")
    result.append("}")
    return result


# used for _all.scad
def genScadMainX(toolpath, toolPathMap, workpieceThickness):
    result = []
    result.extend(getScadWorkPiece(workpieceThickness))
    result.extend(getDxfExample())
    for key, val in toolPathMap.items():
        result.extend(val)
    result.append("")
    result.append("module main () {")
    result.append("  union() {")
    result.append("  % dxf(); ")
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
    result.append("  }")
    result.append("}")
    return result


def buildBox(baseName):
    #
    wName = "{}{}".format(baseName, "_C102Asm")
    boxMillC102Asm = rpi3_box_mill_C102()
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        ofp.write(boxMillC102Asm.genScad())
    log.info("wrote {}".format(scadName))
    gcodeName = "{}{}".format(wName, ".gcode")
    with open(gcodeName, 'w') as ofp:
        ofp.write(boxMillC102Asm.genGcode())
    log.info("wrote {}".format(gcodeName))
    #
    wName = "{}{}".format(baseName, "_C112Asm")
    boxMillC112Asm = rpi3_box_mill_C112()
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        ofp.write(boxMillC112Asm.genScad())
    log.info("wrote {}".format(scadName))
    gcodeName = "{}{}".format(wName, ".gcode")
    with open(gcodeName, 'w') as ofp:
        ofp.write(boxMillC112Asm.genGcode())
    log.info("wrote {}".format(gcodeName))
    #
    toolPathMap = {}
    for asm in (boxMillC102Asm, boxMillC112Asm):
        toolPathMap[asm.name] = asm.genScadToolPath()
    genScadMainCust = partial(genScadMainX,
                              toolPathMap=toolPathMap, 
                              workpieceThickness=WORKPIECE_THICKNESS, )
    wName = "{}{}".format(baseName, "_all")
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        scadAll = gc.scad.genScad(toolMotions=[], cncCfg=None, name="all", main=genScadMainCust)
        ofp.write(str(scadAll))
    log.info("wrote {}".format(scadName))

    

def main(argv):
    baseName = "rpi3_box"
    buildBox(baseName)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
