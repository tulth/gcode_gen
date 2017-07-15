#!/usr/bin/env python
"""Generates gcode that uses nomad 883 to create a box for a rasperry pi 3"""
import sys
import argparse
import logging
import numpy as np
from functools import partial
import rect_pack
import gcode_gen as gc
import common
import gen_simple_box

FAST_SCAD = False
SCAD_SHOW_WORKPIECE = True
#SCAD_SHOW_WORKPIECE = False
SCAD_SHOW_RPI3_CCA = SCAD_SHOW_WORKPIECE

EDGE_MARGIN = 5

FACE_BACKOFF = 0.5  # FIXME not used consistently


log = logging.getLogger()
# log.setLevel(logging.DEBUG)

class SimpleBoxBottomOnly(gen_simple_box.SimpleBox):
    def genny(self):
        print("HERE!!")
        self.gen_face(gen_simple_box.SimpleBox.FACE_BOTTOM)
        #
        rectsToPack = []
        for faceIdx in (gen_simple_box.SimpleBox.FACE_BOTTOM, ):
            width, height = self.faces[faceIdx]['rectBounds']
            print(width, height)
            rect = rect_pack.Rect(0, 0, width, height, data=faceIdx)
            rectsToPack.append(rect)
        packer = rect_pack.RectPack((self.workpieceWidth - EDGE_MARGIN), (self.workpieceHeight - EDGE_MARGIN))
        packer.pack(rectsToPack)
        for rect in packer.packedRectList:
            self.moveHelper(rect.data, rect.x, rect.y, doRot=rect.rotated)
        #
        # FIXME this should be done elsewhere
        for faceIdx in (gen_simple_box.SimpleBox.FACE_BOTTOM, ):
            self.translateFace(faceIdx, *(self.workpieceBotLeft))
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
    
def rpiMountingHolesCuts(toolCutDiameter):
    result = []
    diameter = 2.7
    xOffsets = [3.5 + FACE_BACKOFF]
    xOffsets.append(xOffsets[-1] + 49)
    yOffsets = [3.5 + FACE_BACKOFF]
    yOffsets.append(yOffsets[-1] + 58)
    for yOffset in yOffsets:
        for xOffset in xOffsets:
            verts = gc.shape.poly_circle_verts(32) * diameter / 2
            translate = np.asarray((xOffset, yOffset))  # center
            translateTiled = np.asarray([translate] * len(verts))
            verts += translateTiled
            poly = gc.poly.Polygon(verts).shrinkPoly(toolCutDiameter/2)
            result.append(poly)
    return result


def main2(argv):
    log.setLevel(logging.INFO)
    logHandler = logging.StreamHandler(sys.stdout)
    log.addHandler(logHandler)
    #
    baseName = "rpi3_box_bottom_only"
    boxBaseWidth = 56 + 4 # INTERIOR left face to right face distance
    boxBaseHeight = 85 + 4 # INTERIOR front face to back face distance
    boxBaseDepth = 15.6 + 4.5 + 4  # INTERIOR top face to bottom face distance
    #
    workpieceDepth = 0.2 * gc.number.mmPerInch
    # workpieceDepth = 4
    # workpieceDepth = 3
    postTabThickness = 3
    #
    coarseCutTool=gc.tool.Carbide3D_102()
    #fineCutTool=gc.tool.Mill_0p01mm()
    #fineCutTool=gc.tool.Mill_0p5mm()
    #fineCutTool=gc.tool.Carbide3D_112()
    fineCutTool=gc.tool.Carbide3D_112()
    #
    customFaceCutDict = dict([(face, {"Coarse":[], "Fine":[], }, ) for face in gen_simple_box.SimpleBox.FACES])
    #
    ftd = fineCutTool.cutDiameter
    bottomf = customFaceCutDict[gen_simple_box.SimpleBox.FACE_BOTTOM]["Fine"]
    bottomf.extend(rpiMountingHolesCuts(ftd))
    #
    box = SimpleBoxBottomOnly(name=baseName,
                    interiorWidth=boxBaseWidth,
                    interiorHeight=boxBaseHeight,
                    interiorDepth=boxBaseDepth,
                    workpieceWidth=4 * gc.number.mmPerInch,
                    workpieceHeight=(3 + 1/4)  * gc.number.mmPerInch,
                    workpieceDepth=workpieceDepth,
                    #postTabThickness=0.25 * gc.number.mmPerInch,
                    tabLength=12,
                    postTabThickness=postTabThickness,
                    footWidth=8,
                    footDepth=3,
                    coarseCutTool=coarseCutTool,
                    fineCutTool=fineCutTool,
                    customFaceCutDict=customFaceCutDict,
                    workpieceBotLeft=common.botLeft,
                    )
    box.genny()
    
    return 0

if __name__ == "__main__":
    sys.exit(main2(sys.argv))
