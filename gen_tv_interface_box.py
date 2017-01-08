#!/usr/bin/env python
"""Generates gcode that uses nomad 883 to create a box for my tv interface cca board"""
import sys
import argparse
import logging
import numpy as np
import gcode_gen as gc
import common
from functools import partial

SCAD_SHOW_WORKPIECE = True
SCAD_SHOW_TV_INTERFACE_CCA = SCAD_SHOW_WORKPIECE

log = logging.getLogger()
# log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stdout)
log.addHandler(logHandler)

TOPBOT_WORKPIECE_THICKNESS = (1 / 8) * gc.number.mmPerInch 

MIDDLE_WORKPIECE_THICKNESS = 12.85
WORKPIECE_SIZE = (3 * gc.number.mmPerInch, 3 * gc.number.mmPerInch, MIDDLE_WORKPIECE_THICKNESS)

TV_INTERFACE_CCA_WIDTH = (66.04 - 25.4)  # X direction
TV_INTERFACE_CCA_LENGTH = (46.99 - 25.4)  # Y direction
TV_INTERFACE_CCA_BOT_LEFT = np.asarray((-190.6 + gc.number.mmPerInch, -121.1 - gc.number.mmPerInch - TV_INTERFACE_CCA_LENGTH)) 
TV_INTERFACE_CCA_BOT_LEFT += np.asarray((6, 0, ))  # move right a bit for clean left box edge cut
TV_INTERFACE_CCA_THICKNESS = 0.063 * gc.number.mmPerInch
TV_INTERFACE_CCA_SIZE = np.asarray((TV_INTERFACE_CCA_WIDTH, TV_INTERFACE_CCA_LENGTH))
TV_INTERFACE_CCA_CENTER = TV_INTERFACE_CCA_BOT_LEFT + (TV_INTERFACE_CCA_SIZE / 2)
log.info("TV_INTERFACE_CCA_CENTER {}".format(TV_INTERFACE_CCA_CENTER))

RPI_CONN_TOP_REL_CCA_TOP = -(1.025 - 1) * gc.number.mmPerInch  # Y DIRECTION RELATIVE TO CCA TOP
RPI_CONN_BOT_REL_CCA_TOP = -(1.65 - 1) * gc.number.mmPerInch  # Y DIRECTION RELATIVE TO CCA TOP
RPI_CONN_TOP = RPI_CONN_TOP_REL_CCA_TOP + (TV_INTERFACE_CCA_SIZE[1] / 2)  # Y DIRECTION RELATIVE TO CCA center_y
RPI_CONN_BOT = RPI_CONN_BOT_REL_CCA_TOP + (TV_INTERFACE_CCA_SIZE[1] / 2)   # Y DIRECTION RELATIVE TO CCA center_y
RPI_CONN_CENTER_Y = (RPI_CONN_TOP + RPI_CONN_BOT) / 2  # Y DIRECTION RELATIVE TO CCA center_y
RPI_CONN_LENGTH = (RPI_CONN_TOP - RPI_CONN_BOT)  # Y DIRECTION
RPI_CONN_LENGTH += 1  # add a bit of margin
RPI_CONN_DEPTH = 4.8
RPI_CONN_DEPTH += TV_INTERFACE_CCA_THICKNESS  # account for cca thickness
RPI_CONN_DEPTH += 1  # add a bit of margin

log.info("RPI_CONN_TOP {}".format(RPI_CONN_TOP))
log.info("RPI_CONN_BOT {}".format(RPI_CONN_BOT))

TV_WIRE_CONN_TOP_REL_CCA_TOP = -(1.05 - 1) * gc.number.mmPerInch  # Y DIRECTION RELATIVE TO CCA TOP
TV_WIRE_CONN_BOT_REL_CCA_TOP = -(1.70 - 1) * gc.number.mmPerInch  # Y DIRECTION RELATIVE TO CCA TOP
TV_WIRE_CONN_TOP = TV_WIRE_CONN_TOP_REL_CCA_TOP + (TV_INTERFACE_CCA_SIZE[1] / 2)  # Y DIRECTION RELATIVE TO CCA center_y
TV_WIRE_CONN_BOT = TV_WIRE_CONN_BOT_REL_CCA_TOP + (TV_INTERFACE_CCA_SIZE[1] / 2)   # Y DIRECTION RELATIVE TO CCA center_y
TV_WIRE_CONN_CENTER_Y = (TV_WIRE_CONN_TOP + TV_WIRE_CONN_BOT) / 2  # Y DIRECTION RELATIVE TO CCA center_y
TV_WIRE_CONN_LENGTH = (TV_WIRE_CONN_TOP - TV_WIRE_CONN_BOT)  # Y DIRECTION
TV_WIRE_CONN_LENGTH += 0  # add a bit of margin
APPROX_WIRE_DIA = 0.7620
TV_WIRE_CONN_DEPTH = APPROX_WIRE_DIA
TV_WIRE_CONN_DEPTH += TV_INTERFACE_CCA_THICKNESS  # account for cca thickness
TV_WIRE_CONN_DEPTH += 1  # add a bit of margin

BOX_INTERIOR_CENTER = TV_INTERFACE_CCA_CENTER
BOX_INTERIOR_SIZE = TV_INTERFACE_CCA_SIZE + np.asarray((4, 5))
BOX_INTERIOR_BOT_LEFT = BOX_INTERIOR_CENTER - (BOX_INTERIOR_SIZE / 2)
BOX_WALL_THICKNESS = 0.3 * gc.number.mmPerInch
BOX_EXTERIOR_CENTER = TV_INTERFACE_CCA_CENTER
BOX_EXTERIOR_SIZE = BOX_INTERIOR_SIZE + 2 * np.asarray((BOX_WALL_THICKNESS, BOX_WALL_THICKNESS, ))
BOX_EXTERIOR_BOT_LEFT = BOX_EXTERIOR_CENTER - (BOX_EXTERIOR_SIZE / 2)
log.info("BOX_EXTERIOR_SIZE {}".format(BOX_EXTERIOR_SIZE))


def tv_interface_box_drill_C101(depth=MIDDLE_WORKPIECE_THICKNESS + 2):
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
    asmFile = gc.assembly.FileAsm(name="boxBottomMill_C101", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    # drill holes
    for offset in drlOffsets:
        asm += gc.cut.DrillHole(depth=depth,
                                ).translate(*offset)
    asm.translate(*(BOX_EXTERIOR_SIZE/2.0))
    asm.translate(*BOX_EXTERIOR_BOT_LEFT)
    asm += gc.cmd.G0(z=cncCfg["zSafe"])
    return asmFile

# tv_interface_box_bottom_mill_C101 = tv_interface_box_drill_C101
tv_interface_box_middle_back_mill_C101 = tv_interface_box_drill_C101
tv_interface_box_middle_mill_C101 = tv_interface_box_drill_C101
tv_interface_box_topbot_mill_C101 = tv_interface_box_drill_C101
#tv_interface_box_top_mill_C101 = tv_interface_box_drill_C101 


def getDrillOffsets():
    thicknessDiv=1.65
    drlOffsets = []
    for xNeg in (False, True):
        for yNeg in (False, True):
            xOffset = BOX_EXTERIOR_SIZE[0]/2 - BOX_WALL_THICKNESS / thicknessDiv
            yOffset = BOX_EXTERIOR_SIZE[1]/2 - BOX_WALL_THICKNESS / thicknessDiv
            if xNeg:
                xOffset = -xOffset
            if yNeg:
                yOffset = -yOffset
            drlOffsets.append((xOffset, yOffset))
    return drlOffsets



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



def tv_interface_box_bottom_mill_C112():
    """Mill corner hex holes"""
    comments = []
    comments.append("""tv interface box bottom Mill_C112""")
    comments.append("""mill hex nut for drill screw holes""")
    bit = gc.tool.Carbide3D_112()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         )
    #
    #
    drlOffsets = getDrillOffsets()
    DEPTH = MIDDLE_WORKPIECE_THICKNESS + 2
    asmFile = gc.assembly.FileAsm(name="boxBottomMill_C112", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    # drill holes
    for offset in drlOffsets:
        asm += M3NutCut().translate(*offset)
    asm.translate(*(BOX_EXTERIOR_SIZE/2.0))
    asm.translate(*BOX_EXTERIOR_BOT_LEFT)
    asm += gc.cmd.G0(z=cncCfg["zSafe"])
    return asmFile


def tv_interface_box_middle_mill_C102():
    comments = []
    comments.append("""tv interface box middle Mill_C102""")
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
    # tv wiring cutout
    asm += gc.cut.RectangleToDepth(depth=0.15 * gc.number.mmPerInch,
                                   xWidth=BOX_WALL_THICKNESS + 1,
                                   yLength=TV_WIRE_CONN_LENGTH,
                                   overlap=None,
                                   isDogBone=True,
                                   isOutline=False,
                                   isFilled=True)
    asm.last().translate(BOX_INTERIOR_SIZE[0] / 2 + BOX_WALL_THICKNESS / 2,
                         y=TV_WIRE_CONN_CENTER_Y)
    # rpi cable cutout
    asm += gc.cut.RectangleToDepth(depth=RPI_CONN_DEPTH,
                                   xWidth=BOX_WALL_THICKNESS + 1,
                                   yLength=RPI_CONN_LENGTH,
                                   overlap=None,
                                   isDogBone=True,
                                   isOutline=False,
                                   isFilled=True)
    asm.last().translate(x=-BOX_INTERIOR_SIZE[0] / 2 - BOX_WALL_THICKNESS / 2,
                         y=RPI_CONN_CENTER_Y)
    # interior cut out
    DEPTH = MIDDLE_WORKPIECE_THICKNESS + 0.2
    asm += gc.cut.RectangleToDepth(depth=DEPTH,
                                   xWidth=BOX_INTERIOR_SIZE[0],
                                   yLength=BOX_INTERIOR_SIZE[1],
                                   overlap=None,
                                   isDogBone=True,
                                   isOutline=False,
                                   isFilled=False)
    # exterior cut out
    asm += gc.cut.RectangleToDepth(depth=DEPTH,
                                   xWidth=BOX_EXTERIOR_SIZE[0],
                                   yLength=BOX_EXTERIOR_SIZE[1],
                                   overlap=None,
                                   isDogBone=False,
                                   isOutline=True,
                                   isFilled=False)
    asm.translate(*(BOX_EXTERIOR_SIZE/2.0))
    asm.translate(*BOX_EXTERIOR_BOT_LEFT)
    return asmFile


def tv_interface_box_middle_back_mill_C102():
    comments = []
    comments.append("""tv interface box middle back Mill_C102""")
    bit = gc.tool.Carbide3D_102()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         zMargin=0.5,
                                         )
    #
    asmFile = gc.assembly.FileAsm(name="boxMiddleBackMill_C102", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    # interior cut out
    DEPTH = MIDDLE_WORKPIECE_THICKNESS + 0.2
    asm += gc.cut.RectangleToDepth(depth=DEPTH,
                                   xWidth=BOX_INTERIOR_SIZE[0],
                                   yLength=BOX_INTERIOR_SIZE[1],
                                   overlap=None,
                                   isDogBone=True,
                                   isOutline=False,
                                   isFilled=False)
    # exterior cut out
    asm += gc.cut.RectangleToDepth(depth=DEPTH,
                                   xWidth=BOX_EXTERIOR_SIZE[0],
                                   yLength=BOX_EXTERIOR_SIZE[1],
                                   overlap=None,
                                   isDogBone=False,
                                   isOutline=True,
                                   isFilled=False)
    asm.translate(*(BOX_EXTERIOR_SIZE/2.0))
    asm.translate(*BOX_EXTERIOR_BOT_LEFT)
    return asmFile


def tv_interface_box_topbot_mill_C102():
    comments = []
    comments.append("""tv interface box topbot Mill_C102""")
    bit = gc.tool.Carbide3D_102()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         zMargin=0.5,
                                         )
    #
    asmFile = gc.assembly.FileAsm(name="boxTopbotMill_C102", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    #
    DEPTH = TOPBOT_WORKPIECE_THICKNESS + 0.5
    # interior cut out
    # none!
    # exterior cut out
    asm += gc.cut.RectangleToDepth(depth=DEPTH,
                                   xWidth=BOX_EXTERIOR_SIZE[0],
                                   yLength=BOX_EXTERIOR_SIZE[1],
                                   overlap=None,
                                   isDogBone=False,
                                   isOutline=True,
                                   isFilled=False)
    asm.translate(*(BOX_EXTERIOR_SIZE/2.0))
    asm.translate(*BOX_EXTERIOR_BOT_LEFT)
    return asmFile


def getScadWorkPiece(workpieceThickness):
    result = []
    result.append("module workpiece() {")
    result.append("  translate([{}, {}, {}]) ".format(*common.botLeft, -workpieceThickness))
    result.append("  cube([{}, {}, {}]);".format(WORKPIECE_SIZE[0], WORKPIECE_SIZE[1], workpieceThickness))
    result.append("}")
    result.append("")
    return result
    

def getScadTvInterfaceCCA():
    result = []
    result.append("module tv_interface_cca() {")
    result.append('  color("green") ')
    result.append("  translate([{}, {}, {}]) ".format(*TV_INTERFACE_CCA_BOT_LEFT, 0 + 1))
    result.append("  cube([{}, {}, {}]);".format(*TV_INTERFACE_CCA_SIZE, TV_INTERFACE_CCA_THICKNESS))
    result.append("}")
    result.append("")
    return result


# used for scad layers EXCEPT FOR _all.scad
def genScadMain(toolPathName):
    result = []
    result.extend(getScadWorkPiece(workpieceThickness=MIDDLE_WORKPIECE_THICKNESS))  # FIXME
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
def genScadMainX(toolpath, toolPathMap, workpieceThickness):
    result = []
    result = []
    result.extend(getScadWorkPiece(workpieceThickness))
    result.extend(getScadTvInterfaceCCA())
    for key, val in toolPathMap.items():
        result.extend(val)
    result.append("")
    result.append("module main () {")
    result.append("  union() {")
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
    if SCAD_SHOW_TV_INTERFACE_CCA:
        result.append("    tv_interface_cca();")
    result.append("  }")
    result.append("}")
    return result


def buildBoxMiddle(baseName):
    #
    wName = "{}{}".format(baseName, "_middle_C101Asm_DONTUSE")
    boxMiddleMillC101Asm = tv_interface_box_middle_mill_C101(depth=MIDDLE_WORKPIECE_THICKNESS + 8)  # go deep here to use as alignment holes for flip and cut hex inserts
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
    boxMiddleMillC102Asm = tv_interface_box_middle_mill_C102()
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
                              toolPathMap=toolPathMap,
                              workpieceThickness=MIDDLE_WORKPIECE_THICKNESS, )
    wName = "{}{}".format(baseName, "_middle_all")
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        scadAll = gc.scad.genScad(toolMotions=[], cncCfg=None, name="all", main=genScadMainCust)
        ofp.write(str(scadAll))
    log.info("wrote {}".format(scadName))

    
def buildBoxMiddleBack(baseName):
    #
    wName = "{}{}".format(baseName, "_middle_back_C101Asm")
    boxMiddleBackMillC101Asm = tv_interface_box_middle_mill_C101(depth=MIDDLE_WORKPIECE_THICKNESS + 8)  # go deep here to use as alignment holes for flip and cut hex inserts
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        ofp.write(boxMiddleBackMillC101Asm.genScad())
    log.info("wrote {}".format(scadName))
    gcodeName = "{}{}".format(wName, ".gcode")
    with open(gcodeName, 'w') as ofp:
        ofp.write(boxMiddleBackMillC101Asm.genGcode())
    log.info("wrote {}".format(gcodeName))
    #
    wName = "{}{}".format(baseName, "_middle_back_C102Asm_DONTUSE")
    boxMiddleBackMillC102Asm = tv_interface_box_middle_back_mill_C102()
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        ofp.write(boxMiddleBackMillC102Asm.genScad())
    log.info("wrote {}".format(scadName))
    gcodeName = "{}{}".format(wName, ".gcode")
    with open(gcodeName, 'w') as ofp:
        ofp.write(boxMiddleBackMillC102Asm.genGcode())
    log.info("wrote {}".format(gcodeName))
    #
    wName = "{}{}".format(baseName, "_middle_back_C112Asm")
    boxMiddleBackMillC112Asm = tv_interface_box_middle_back_mill_C112()
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        ofp.write(boxMiddleBackMillC112Asm.genScad())
    log.info("wrote {}".format(scadName))
    gcodeName = "{}{}".format(wName, ".gcode")
    with open(gcodeName, 'w') as ofp:
        ofp.write(boxMiddleBackMillC112Asm.genGcode())
    log.info("wrote {}".format(gcodeName))
    #
    toolPathMap = {}
    for asm in (boxMiddleBackMillC101Asm, boxMiddleBackMillC102Asm, boxMiddleBackMillC112Asm):
        toolPathMap[asm.name] = asm.genScadToolPath()
    genScadMainCust = partial(genScadMainX,
                              toolPathMap=toolPathMap, 
                              workpieceThickness=MIDDLE_WORKPIECE_THICKNESS, )
    wName = "{}{}".format(baseName, "_middle_back_all")
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        scadAll = gc.scad.genScad(toolMotions=[], cncCfg=None, name="all", main=genScadMainCust)
        ofp.write(str(scadAll))
    log.info("wrote {}".format(scadName))
    

def buildBoxTopBot(baseName):
    #
    wName = "{}{}".format(baseName, "_topbot_C101Asm")
    boxTopbotMillC101Asm = tv_interface_box_topbot_mill_C101(depth=TOPBOT_WORKPIECE_THICKNESS + 2) 
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        ofp.write(boxTopbotMillC101Asm.genScad())
    log.info("wrote {}".format(scadName))
    gcodeName = "{}{}".format(wName, ".gcode")
    with open(gcodeName, 'w') as ofp:
        ofp.write(boxTopbotMillC101Asm.genGcode())
    log.info("wrote {}".format(gcodeName))
    #
    wName = "{}{}".format(baseName, "_topbot_C102Asm")
    boxTopbotMillC102Asm = tv_interface_box_topbot_mill_C102()
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        ofp.write(boxTopbotMillC102Asm.genScad())
    log.info("wrote {}".format(scadName))
    gcodeName = "{}{}".format(wName, ".gcode")
    with open(gcodeName, 'w') as ofp:
        ofp.write(boxTopbotMillC102Asm.genGcode())
    log.info("wrote {}".format(gcodeName))
    #
    toolPathMap = {}
    for asm in (boxTopbotMillC101Asm, boxTopbotMillC102Asm):
        toolPathMap[asm.name] = asm.genScadToolPath()
    genScadMainCust = partial(genScadMainX,
                              toolPathMap=toolPathMap, 
                              workpieceThickness=TOPBOT_WORKPIECE_THICKNESS, )
    wName = "{}{}".format(baseName, "_topbot_all")
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        scadAll = gc.scad.genScad(toolMotions=[], cncCfg=None, name="all", main=genScadMainCust)
        ofp.write(str(scadAll))
    log.info("wrote {}".format(scadName))

    
def tv_interface_box_middle_back_mill_C112():
    """Mill corner hex holes"""
    comments = []
    comments.append("""tv interface box middleBack Mill_C112""")
    comments.append("""drill screw holes""")
    bit = gc.tool.Carbide3D_112()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         )
    #
    #
    drlOffsets = getDrillOffsets()
    DEPTH = MIDDLE_WORKPIECE_THICKNESS + 2
    asmFile = gc.assembly.FileAsm(name="boxMiddleBackMill_C112", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    # drill holes
    for offset in drlOffsets:
        asm += M3NutCut().translate(*offset)
    asm.translate(*(BOX_EXTERIOR_SIZE/2.0))
    asm.translate(*BOX_EXTERIOR_BOT_LEFT)
    asm += gc.cmd.G0(z=cncCfg["zSafe"])
    return asmFile


def main(argv):
    baseName = "tv_interface_box"
    buildBoxMiddleBack(baseName)
    buildBoxMiddle(baseName)
    buildBoxTopBot(baseName)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
