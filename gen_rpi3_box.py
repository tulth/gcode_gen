#!/usr/bin/env python
"""Generates gcode that uses nomad 883 to create a box for a rasperry pi 3"""
import sys
import argparse
import logging
import numpy as np
import gcode_gen as gc
import common
from gen_simple_box import *  # FIXME


# FAST_SCAD = True
FAST_SCAD = False
SCAD_SHOW_WORKPIECE = True
#SCAD_SHOW_WORKPIECE = False
SCAD_SHOW_RPI3_CCA = SCAD_SHOW_WORKPIECE

EDGE_MARGIN = 5

FACE_BACKOFF = 0.5  # FIXME not used consistently


log = logging.getLogger()
# log.setLevel(logging.DEBUG)

def ethernetCut(toolCutDiameter, xTrans=10.25 + FACE_BACKOFF):
    ethWidth = 16.5566
    ethXOffset = xTrans
    ethXs = (ethXOffset - ethWidth / 2,  ethXOffset + ethWidth / 2)
    ethYs = (11.694 + 5 - 13.02294, 26.304 + 5 - 13.02294, )
    verts = np.asarray(((ethXs[0], ethYs[0]),
                        (ethXs[1], ethYs[0]),
                        (ethXs[1], ethYs[1]),
                        (ethXs[0], ethYs[1]),
                        ))
    ethPolyPerim = gc.poly.PolygonInsideDogbone(verts, shrinkAmount=toolCutDiameter/2, )
    return ethPolyPerim


def usbCut(toolCutDiameter, xTrans, yTrans):
    usbWidth = 16.5
    usbXs = (xTrans - usbWidth / 2,  xTrans + usbWidth / 2)
    usbHeight = 17.9641
    usbYs = (yTrans - usbHeight / 2,  yTrans + usbHeight / 2)
    verts = np.asarray(((usbXs[0], usbYs[0]),
                        (usbXs[1], usbYs[0]),
                        (usbXs[1], usbYs[1]),
                        (usbXs[0], usbYs[1]),
                        ))
    # boxBotLeftTiled = np.asarray([boxBotLeft] * len(verts))
    # verts -= boxBotLeftTiled
    polyPerim = gc.poly.Polygon(vertices=verts, ).shrinkPoly(toolCutDiameter/2)
    return polyPerim


def usb0Cut(toolCutDiameter):
    return usbCut(toolCutDiameter, 29 + FACE_BACKOFF, 12.57)


def usb1Cut(toolCutDiameter):
    return usbCut(toolCutDiameter, 47 + FACE_BACKOFF, 12.57)


def powerCut(toolCutDiameter):
    cutXs = (90.2892, 102.2215, )
    cutYs = (14.3817, 23.3251)
    verts = np.asarray(((cutXs[0], cutYs[0]),
                        (cutXs[1], cutYs[0]),
                        (cutXs[1], cutYs[1]),
                        (cutXs[0], cutYs[1]),
                        ))
    boxBotLeft = np.asarray((85.5528, 13.02294, ))
    boxBotLeftTiled = np.asarray([boxBotLeft] * len(verts))
    verts -= boxBotLeftTiled
    cutPolyPerim = gc.poly.PolygonInsideDogbone(verts, shrinkAmount=toolCutDiameter/2, )
    return cutPolyPerim


def hdmiCut(toolCutDiameter):
    hdmiXs = (109.586-1, 112.109, 123.279, 125.805+1, )
    hdmiYs = (17.8213, 19.8139, 24.3477)
    verts = np.asarray(((hdmiXs[0], hdmiYs[1]),
                        (hdmiXs[1], hdmiYs[0]),
                        (hdmiXs[2], hdmiYs[0]),
                        (hdmiXs[3], hdmiYs[1]),
                        (hdmiXs[3], hdmiYs[2]),
                        (hdmiXs[0], hdmiYs[2]),
                        ))
    boxBotLeft = np.asarray((85.5528, 13.02294, ))
    boxBotLeftTiled = np.asarray([boxBotLeft] * len(verts))
    verts -= boxBotLeftTiled
    cutPolyPerim = gc.poly.PolygonInsideDogbone(verts, shrinkAmount=toolCutDiameter/2, )
    return cutPolyPerim

def compositeAvCut(toolCutDiameter):
    centerX = (133.513 + 145.437) / 2
    centerY = (26.332 + 14.40788) / 2
    diameter = 11.924
    verts = gc.shape.poly_circle_verts(32) * diameter / 2
    boxBotLeft = np.asarray((85.5528, 13.02294, ))
    translate = -boxBotLeft + np.asarray((centerX, centerY))
    translateTiled = np.asarray([translate] * len(verts))
    verts += translateTiled
    avPoly = gc.poly.Polygon(verts).shrinkPoly(toolCutDiameter/2)
    return avPoly

def sdCardCut(toolCutDiameter):
    sdCardXs = (22.25, 24.5166, 32.4541, 34.7114)
    #sdCardYs = (0, (1/8) * gc.number.mmPerInch * 1.05, 3.246)
    sdCardYs = (0, 1.7, 3.4)
    verts = np.asarray(((sdCardXs[0], sdCardYs[1]),
                        (sdCardXs[1], sdCardYs[0]),
                        (sdCardXs[2], sdCardYs[0]),
                        (sdCardXs[3], sdCardYs[1]),
                        (sdCardXs[3], sdCardYs[2]),
                        (sdCardXs[0], sdCardYs[2]),
                        ))
    cutPolyPerim = gc.poly.Polygon(verts).shrinkPoly(toolCutDiameter/2, )
    return cutPolyPerim

def airVentCuts(toolCutDiameter, xCenter, yCenter):
    # air vent cut out
    ventCutLen = 50
    ventYs = (yCenter - ventCutLen / 2, yCenter + ventCutLen / 2)
    result = []
    for xNum in range(5):
        xOffset = (xNum - 2) * 2.5 * toolCutDiameter
        ventX = xCenter + xOffset
        verts = np.asarray([[ventX, ventYs[0]], [ventX, ventYs[1]]])
        # FIXME
        class PseudoPolygon(object):
            def __init__(self, vertices):
                self.vertices = vertices
        result.append(PseudoPolygon(verts))
    return result


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


def hatCableRoutingCut(toolCutDiameter, boxWidth, boxDepth, workpieceDepth, postTabThickness):
    xCenter, yCenter = np.asarray((boxWidth, boxDepth)) / 2
    cutTop = yCenter + boxDepth / 2 + workpieceDepth + postTabThickness + toolCutDiameter/2
    cutBottom = cutTop - 10
    cutLeft = xCenter - 10
    cutRight = xCenter + 10
    verts = np.asarray(((cutLeft, cutBottom),
                        (cutRight, cutBottom),
                        (cutRight, cutTop),
                        (cutLeft, cutTop),
                        ))
    poly = gc.poly.Polygon(verts).shrinkPoly(toolCutDiameter/2, )
    #poly = gc.poly.PolygonInsideDogbone(verts, shrinkAmount=toolCutDiameter/2, )
    return poly


def main(argv):
    log.setLevel(logging.INFO)
    logHandler = logging.StreamHandler(sys.stdout)
    log.addHandler(logHandler)
    #
    baseName = "rpi3_box"
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
    customFaceCutDict = dict([(face, {"Coarse":[], "Fine":[], }, ) for face in SimpleBox.FACES])
    #
    ftd = fineCutTool.cutDiameter
    frontf = customFaceCutDict[SimpleBox.FACE_FRONT]["Fine"]
    frontf.append(sdCardCut(ftd))
    bottomf = customFaceCutDict[SimpleBox.FACE_BOTTOM]["Fine"]
    bottomf.extend(rpiMountingHolesCuts(ftd))
    #
    ctd = coarseCutTool.cutDiameter
    topc = customFaceCutDict[SimpleBox.FACE_TOP]["Coarse"]
    topc.extend(airVentCuts(ctd, boxBaseWidth/2, boxBaseHeight/2, ))
    backc = customFaceCutDict[SimpleBox.FACE_BACK]["Coarse"]
    backc.append(ethernetCut(ctd))
    backc.append(usb0Cut(ctd))
    backc.append(usb1Cut(ctd))
    backc.append(hatCableRoutingCut(ctd, boxBaseWidth, boxBaseDepth, workpieceDepth, postTabThickness))
    rightc = customFaceCutDict[SimpleBox.FACE_RIGHT]["Coarse"]
    rightc.append(powerCut(ctd))
    rightc.append(hdmiCut(ctd))
    rightc.append(compositeAvCut(ctd))
    #
    box = SimpleBox(name=baseName,
                    interiorWidth=boxBaseWidth,
                    interiorHeight=boxBaseHeight,
                    interiorDepth=boxBaseDepth,
                    workpieceWidth=8 * gc.number.mmPerInch,
                    workpieceHeight=8 * gc.number.mmPerInch,
                    workpieceDepth=workpieceDepth,
                    #postTabThickness=0.25 * gc.number.mmPerInch,
                    tabLength=12,
                    postTabThickness=postTabThickness,
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
