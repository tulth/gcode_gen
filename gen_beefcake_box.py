#!/usr/bin/env python
"""Generates gcode for drilling nomad 883 bottom left alignment pin holes"""
import sys
import argparse
import logging
import numpy as np
import gcode_gen as gc
import common
from functools import partial

SCAD_SHOW_WORKPIECE = True

log = logging.getLogger()
# log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stdout)
log.addHandler(logHandler)

WORKPIECE_THICKNESS = 12.85
WORKPIECE_SIZE = (4 * gc.number.mmPerInch, 3 * gc.number.mmPerInch, WORKPIECE_THICKNESS)

CENTERS = (((3 - 0.125) * gc.number.mmPerInch, (2 - 0.125) * gc.number.mmPerInch),
           ((0.125) * gc.number.mmPerInch, (0.125) * gc.number.mmPerInch), )


BEEFCAKE_LENGTH = 28.0 + 2  # add few mm margin
BEEFCAKE_WIDTH = 61.0 + 2

BEEFCAKE_SIZE = np.asarray((BEEFCAKE_WIDTH, BEEFCAKE_LENGTH, ))
BOX_THICKNESS = 0.4 * gc.number.mmPerInch

BOX_BOT_LEFT = np.asarray(common.botLeft) + (np.asarray((0.4, 0.4, )) * gc.number.mmPerInch)
BOARD_BOT_LEFT = BOX_BOT_LEFT + np.asarray((BOX_THICKNESS, BOX_THICKNESS, ))

BOX_SIZE =  BEEFCAKE_SIZE + 2 * np.asarray((BOX_THICKNESS, BOX_THICKNESS, ))

def beefcake_box_bottom_mill_C101():
    """Drill corner holes"""
    comments = []
    comments.append("""drill screw holes""")
    bit = gc.tool.Carbide3D_101()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         )
    #
    drlOffsets = getDrillOffsets()
    DEPTH = WORKPIECE_THICKNESS + 2
    asmFile = gc.assembly.FileAsm(name="boxBottomMill_C101", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    # drill holes
    for offset in drlOffsets:
        asm += gc.cut.DrillHole(depth=DEPTH,
                                ).translate(*offset)
    asm.translate(*(BOX_SIZE/2.0))
    asm.translate(*BOX_BOT_LEFT)
    asm += gc.cmd.G0(z=cncCfg["zSafe"])
    return asmFile

beefcake_box_middle_mill_C101 = beefcake_box_bottom_mill_C101
beefcake_box_top_mill_C101 = beefcake_box_bottom_mill_C101


def getDrillOffsets():
    drlOffsets = []
    for xNeg in (False, True):
        for yNeg in (False, True):
            xOffset = BOX_SIZE[0]/2 - BOX_THICKNESS / 2
            if xNeg:
                xOffset = -xOffset
            yOffset = BOX_SIZE[1]/2 - BOX_THICKNESS / 2
            if yNeg:
                yOffset = -yOffset
            drlOffsets.append((xOffset, yOffset))
    return drlOffsets


def beefcake_box_bottom_mill_C102():
    comments = []
    comments.append("""beefcake bottom Mill_C102""")
    comments.append("""cut box outline""")
    bit = gc.tool.Carbide3D_102()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         )
    #
    DEPTH = WORKPIECE_THICKNESS + 0.2
    asmFile = gc.assembly.FileAsm(name="boxBottomMill_C102", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    # interior cut
    # None for now
    # exterior cut
    asm += gc.cut.RectangleToDepth(depth=DEPTH,
                                   xWidth=BOX_SIZE[0],
                                   yLength=BOX_SIZE[1],
                                   overlap=None,
                                   isDogBone=False,
                                   isOutline=True,
                                   isFilled=False)
    asm.translate(*(BOX_SIZE/2.0))
    asm.translate(*BOX_BOT_LEFT)
    asm += gc.cmd.G0(z=cncCfg["zSafe"])
    return asmFile


class M3NutCut(gc.assembly.Assembly):
    def _elab(self,
              overlap=None):
        M3_NUT_FACE2FACE = 0.215 * gc.number.mmPerInch
        M3_NUT_HEIGHT = 0.096 * gc.number.mmPerInch
        if overlap is None:
            overlap = self.cncCfg["defaultMillingOverlap"]
        self += gc.cmd.G0(z=self.cncCfg["zSafe"])
        self += gc.cmd.G0(*self.center[0:2])
        self += gc.cut.HexagonToDepth(depth=M3_NUT_HEIGHT,
                                      faceToFace=M3_NUT_FACE2FACE,
                                      isDogBone=True,
                                      isFilled=True,
                                      overlap=overlap)
        self += gc.cmd.G0(*self.center[0:2])
        self += gc.cmd.G0(z=self.cncCfg["zSafe"])



def beefcake_box_bottom_mill_C112():
    """Mill corner hex holes"""
    comments = []
    comments.append("""beefcake bottom Mill_C112""")
    comments.append("""drill screw holes""")
    bit = gc.tool.Carbide3D_112()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         )
    #
    #
    drlOffsets = getDrillOffsets()
    DEPTH = WORKPIECE_THICKNESS + 2
    asmFile = gc.assembly.FileAsm(name="boxBottomMill_C112", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    # drill holes
    for offset in drlOffsets:
        asm += M3NutCut().translate(*offset)
    asm.translate(*(BOX_SIZE/2.0))
    asm.translate(*BOX_BOT_LEFT)
    asm += gc.cmd.G0(z=cncCfg["zSafe"])
    return asmFile


def beefcake_box_middle_mill_C102():
    comments = []
    comments.append("""beefcake middle Mill_C102""")
    bit = gc.tool.Carbide3D_102()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         zMargin=0.5,
                                         )
    #
    asmFile = gc.assembly.FileAsm(name="boxMiddleMill_C102", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    # control cable cutout
    asm += gc.cut.RectangleToDepth(depth=0.15 * gc.number.mmPerInch,
                                   xWidth=BOX_THICKNESS,
                                   yLength=0.5 * gc.number.mmPerInch,
                                   overlap=None,
                                   isDogBone=True,
                                   isOutline=False,
                                   isFilled=True)
    asm.last().translate(BEEFCAKE_SIZE[0] / 2 + BOX_THICKNESS / 2, 0)
    # power cable cutouts
    AC_CABLE_SLOTSIZE = 0.34 * gc.number.mmPerInch + 2
    for upperCable in (True, False):
        asm += gc.cut.RectangleToDepth(depth=AC_CABLE_SLOTSIZE,
                                       xWidth=AC_CABLE_SLOTSIZE,
                                       yLength=BOX_THICKNESS,
                                       overlap=None,
                                       isDogBone=True,
                                       isOutline=False,
                                       isFilled=True)
        yOffset = BEEFCAKE_SIZE[1] / 2 + BOX_THICKNESS / 2
        AC_CABLE_BOARD_XOFFSET = 5
        xOffset = -BEEFCAKE_SIZE[0] / 2 + AC_CABLE_SLOTSIZE / 2 + AC_CABLE_BOARD_XOFFSET
        if not upperCable:
            yOffset = -yOffset
        asm.last().translate(xOffset, yOffset)
    # interior cut out
    DEPTH = WORKPIECE_THICKNESS + 0.2
    asm += gc.cut.RectangleToDepth(depth=DEPTH,
                                   xWidth=BEEFCAKE_SIZE[0],
                                   yLength=BEEFCAKE_SIZE[1],
                                   overlap=None,
                                   isDogBone=True,
                                   isOutline=False,
                                   isFilled=False)
    # exterior cut out
    asm += gc.cut.RectangleToDepth(depth=DEPTH,
                                   xWidth=BOX_SIZE[0],
                                   yLength=BOX_SIZE[1],
                                   overlap=None,
                                   isDogBone=False,
                                   isOutline=True,
                                   isFilled=False)
    asm.translate(*(BOX_SIZE/2.0))
    asm.translate(*BOX_BOT_LEFT)
    return asmFile


def genScadMain(toolPathName):
    result = []
    result.append("module workpiece() {")
    result.append("  translate([{}, {}, {}]) ".format(*common.botLeft, -WORKPIECE_THICKNESS))
    result.append("  cube([{}, {}, {}]);".format(*WORKPIECE_SIZE))
    result.append("}")
    result.append("")
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

def genScadMainX(toolpath, toolPathMap, ):
    result = []
    result.append("module workpiece() {")
    result.append("  translate([{}, {}, {}]) ".format(*common.botLeft, -WORKPIECE_THICKNESS))
    result.append("  cube([{}, {}, {}]);".format(*WORKPIECE_SIZE))
    result.append("}")
    result.append("")
    for key, val in toolPathMap.items():
        result.extend(val)
    result.append("module main () {")
    if SCAD_SHOW_WORKPIECE:
        result.append("  difference() {")
        result.append("    workpiece();")
    result.append("    union() {")
    for key in toolPathMap:
        result.append("      {}();".format(gc.scad.makeToolPathName(key)))
    if SCAD_SHOW_WORKPIECE:
        result.append("    }")
    result.append("  }")
    result.append("}")
    return result


def buildBoxBottom(baseName):
    #
    wName = "{}{}".format(baseName, "_bottom_C101Asm")
    boxBottomMillC101Asm = beefcake_box_bottom_mill_C101()
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        ofp.write(boxBottomMillC101Asm.genScad())
    log.info("wrote {}".format(scadName))
    gcodeName = "{}{}".format(wName, ".gcode")
    with open(gcodeName, 'w') as ofp:
        ofp.write(boxBottomMillC101Asm.genGcode())
    log.info("wrote {}".format(gcodeName))
    #
    wName = "{}{}".format(baseName, "_bottom_C102Asm")
    boxBottomMillC102Asm = beefcake_box_bottom_mill_C102()
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        ofp.write(boxBottomMillC102Asm.genScad())
    log.info("wrote {}".format(scadName))
    gcodeName = "{}{}".format(wName, ".gcode")
    with open(gcodeName, 'w') as ofp:
        ofp.write(boxBottomMillC102Asm.genGcode())
    log.info("wrote {}".format(gcodeName))
    #
    wName = "{}{}".format(baseName, "_bottom_C112Asm")
    boxBottomMillC112Asm = beefcake_box_bottom_mill_C112()
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        ofp.write(boxBottomMillC112Asm.genScad())
    log.info("wrote {}".format(scadName))
    gcodeName = "{}{}".format(wName, ".gcode")
    with open(gcodeName, 'w') as ofp:
        ofp.write(boxBottomMillC112Asm.genGcode())
    log.info("wrote {}".format(gcodeName))
    #
    toolPathMap = {}
    for asm in (boxBottomMillC101Asm, boxBottomMillC102Asm, boxBottomMillC112Asm):
        toolPathMap[asm.name] = asm.genScadToolPath()
    genScadMainCust = partial(genScadMainX,
                              toolPathMap=toolPathMap, )
    wName = "{}{}".format(baseName, "_bottom_all")
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        scadAll = gc.scad.genScad(toolMotions=[], cncCfg=None, name="all", main=genScadMainCust)
        ofp.write(str(scadAll))
    log.info("wrote {}".format(scadName))

    
def buildBoxMiddle(baseName):
    #
    wName = "{}{}".format(baseName, "_middle_C101Asm")
    boxMiddleMillC101Asm = beefcake_box_middle_mill_C101()
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        ofp.write(boxMiddleMillC101Asm.genScad())
    log.info("wrote {}".format(scadName))
    gcodeName = "{}{}".format(wName, ".gcode")
    with open(gcodeName, 'w') as ofp:
        ofp.write(boxMiddleMillC101Asm.genGcode())
    log.info("wrote {}".format(gcodeName))
    #
    wName = "{}{}".format(baseName, "_middle_C102Asm")
    boxMiddleMillC102Asm = beefcake_box_middle_mill_C102()
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        ofp.write(boxMiddleMillC102Asm.genScad())
    log.info("wrote {}".format(scadName))
    gcodeName = "{}{}".format(wName, ".gcode")
    with open(gcodeName, 'w') as ofp:
        ofp.write(boxMiddleMillC102Asm.genGcode())
    log.info("wrote {}".format(gcodeName))
    #
    toolPathMap = {}
    for asm in (boxMiddleMillC101Asm, boxMiddleMillC102Asm):
        toolPathMap[asm.name] = asm.genScadToolPath()
    genScadMainCust = partial(genScadMainX,
                              toolPathMap=toolPathMap, )
    wName = "{}{}".format(baseName, "_middle_all")
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        scadAll = gc.scad.genScad(toolMotions=[], cncCfg=None, name="all", main=genScadMainCust)
        ofp.write(str(scadAll))
    log.info("wrote {}".format(scadName))


class RelayShape(gc.shape.BaseShape):
    def _elab(self,
              overlap=None):
        xSteps = np.asarray((0.408, 0.408 + 0.57, 0.408 + 0.745, 0.408 + 1.25)) * gc.number.mmPerInch
        ySteps = np.asarray((0, 0.195, 0.195 + 0.77, 1.055)) * gc.number.mmPerInch
        dr = self.cncCfg["tool"].cutDiameter / 2.0
        vertices = np.asarray(((xSteps[2] + dr, ySteps[0] + dr),
                               (xSteps[3] - dr, ySteps[0] + dr),
                               (xSteps[3] - dr, ySteps[3] - dr),
                               (xSteps[1] + dr, ySteps[3] - dr),
                               (xSteps[1] + dr, ySteps[2] - dr),
                               (xSteps[1]     , ySteps[2]     ),
                               (xSteps[1] + dr, ySteps[2] - dr),
                               (xSteps[0] + dr, ySteps[2] - dr),
                               (xSteps[0] + dr, ySteps[1] + dr),
                               (xSteps[2] + dr, ySteps[1] + dr),
                               (xSteps[2]     , ySteps[1]     ),
                               (xSteps[2] + dr, ySteps[1] + dr),
                               ))
        vertices = self.transforms.doTransform(vertices)
        for v in vertices:
            self += gc.cmd.G1(*v)
        self += gc.cmd.G1(*vertices[0])
        # already did transforms on verts, before passing to children so don't transform children!
        self.transforms = gc.hg_coords.TransformList() 

        
class RelayCut(gc.assembly.Assembly):
    def _elab(self,
              depth,
              overlap=None):
        zCutSteps = gc.number.calcZSteps(0, -depth, self.cncCfg["defaultDepthPerMillingPass"])
        self += gc.cmd.G0(x=self.center[0], y=self.center[1])
        zStart = self.center[2] + self.cncCfg["zMargin"]
        self += gc.cmd.G0(z=zStart)
        for zCutStep in zCutSteps:
            self += RelayShape()
            self.last().translate(z=zCutStep)
        self += gc.cmd.G0(z=zStart)
    
def beefcake_box_top_mill_C102():
    comments = []
    comments.append("""beefcake top Mill_C102""")
    comments.append("""cut box outline""")
    bit = gc.tool.Carbide3D_102()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         )
    #
    DEPTH = WORKPIECE_THICKNESS + 0.2
    asmFile = gc.assembly.FileAsm(name="boxTopMill_C102", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    # cut recess for screws
    M3_SCREW_HEAD_DIAMETER = 5.6
    M3_SCREW_HEAD_DEPTH = 3
    for offset in getDrillOffsets():
        asm += gc.cut.Cylinder(depth=M3_SCREW_HEAD_DEPTH,
                                diameter=M3_SCREW_HEAD_DIAMETER, ).translate(*offset)
        asm += gc.cmd.G0(z=cncCfg["zSafe"])
    
    # cut hole for LED
    LED_HOLE_DIA = 0.194 * gc.number.mmPerInch
    LED_HOLE_OFFSET = np.asarray((1.95, 0.166)) * gc.number.mmPerInch
    asm += gc.cut.Cylinder(depth=DEPTH,
                           diameter=LED_HOLE_DIA, ).translate(*LED_HOLE_OFFSET)
    asm.last().translate(*(BEEFCAKE_SIZE * -0.5))
    asm += gc.cmd.G0(z=cncCfg["zSafe"])
    # cut hole for relay
    asm += RelayCut(DEPTH)
    asm.last().translate(*(BEEFCAKE_SIZE * -0.5))
    asm += gc.cmd.G0(z=cncCfg["zSafe"])
    # exterior cut
    asm += gc.cut.RectangleToDepth(depth=DEPTH,
                                   xWidth=BOX_SIZE[0],
                                   yLength=BOX_SIZE[1],
                                   overlap=None,
                                   isDogBone=False,
                                   isOutline=True,
                                   isFilled=False)
    asm.translate(*(BOX_SIZE/2.0))
    asm.translate(*BOX_BOT_LEFT)
    asm += gc.cmd.G0(z=cncCfg["zSafe"])
    return asmFile
    
def buildBoxTop(baseName):
    #
    wName = "{}{}".format(baseName, "_top_C101Asm")
    boxTopMillC101Asm = beefcake_box_top_mill_C101()
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        ofp.write(boxTopMillC101Asm.genScad())
    log.info("wrote {}".format(scadName))
    gcodeName = "{}{}".format(wName, ".gcode")
    with open(gcodeName, 'w') as ofp:
        ofp.write(boxTopMillC101Asm.genGcode())
    log.info("wrote {}".format(gcodeName))
    #
    wName = "{}{}".format(baseName, "_top_C102Asm")
    boxTopMillC102Asm = beefcake_box_top_mill_C102()
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        ofp.write(boxTopMillC102Asm.genScad())
    log.info("wrote {}".format(scadName))
    gcodeName = "{}{}".format(wName, ".gcode")
    with open(gcodeName, 'w') as ofp:
        ofp.write(boxTopMillC102Asm.genGcode())
    log.info("wrote {}".format(gcodeName))
    #
    toolPathMap = {}
    for asm in (boxTopMillC101Asm, boxTopMillC102Asm):
        toolPathMap[asm.name] = asm.genScadToolPath()
    genScadMainCust = partial(genScadMainX,
                              toolPathMap=toolPathMap, )
    wName = "{}{}".format(baseName, "_top_all")
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        scadAll = gc.scad.genScad(toolMotions=[], cncCfg=None, name="all", main=genScadMainCust)
        ofp.write(str(scadAll))
    log.info("wrote {}".format(scadName))

    
def main(argv):
    baseName = "beefcake_box"
    buildBoxBottom(baseName)
    buildBoxMiddle(baseName)
    buildBoxTop(baseName)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
