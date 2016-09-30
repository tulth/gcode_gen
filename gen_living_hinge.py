#!/usr/bin/env python
"""Generates gcode for drilling a living hinge"""
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

WORKPIECE_THICKNESS = (1 / 8) * gc.number.mmPerInch
WORKPIECE_SIZE = (8 * gc.number.mmPerInch, 4 * gc.number.mmPerInch, WORKPIECE_THICKNESS)

OUTLINE_BOT_LEFT = np.asarray(common.botLeft) + (np.asarray((0.2, 0.2, )) * gc.number.mmPerInch)

OUTLINE_SIZE = np.asarray((100.0, 50.0))

DEPTH = WORKPIECE_THICKNESS + 0.2

def living_hingemill_C102():
    comments = []
    comments.append("""Mill_C102""")
    comments.append("""cut outline""")
    bit = gc.tool.Carbide3D_102()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=10,
                                         zMargin=0.5,
                                         )
    #
    asmFile = gc.assembly.FileAsm(name="boxBottomMill_C102", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    # interior cut
    # None for now
    # exterior cut
    asm += gc.cut.RectangleToDepth(depth=DEPTH,
                                   xWidth=OUTLINE_SIZE[0],
                                   yLength=OUTLINE_SIZE[1],
                                   overlap=None,
                                   isDogBone=False,
                                   isOutline=True,
                                   isFilled=False)
    asm.translate(*(OUTLINE_SIZE/2.0))
    asm.translate(*OUTLINE_BOT_LEFT)
    asm += gc.cmd.G0(z=cncCfg["zSafe"])
    return asmFile



def living_hingemill_C112():
    comments = []
    comments.append("""Mill_C112""")
    comments.append("""Mill living hinge""")
    bit = gc.tool.Carbide3D_112()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=10,
                                         zMargin=0.5,
                                         )
    #
    #
    asmFile = gc.assembly.FileAsm(name="boxBottomMill_C112", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    asm += LivingHingeCut(numPairs=7, depth=DEPTH)
    asm.translate(*(OUTLINE_SIZE/2.0))
    asm.translate(*OUTLINE_BOT_LEFT)
    asm += gc.cmd.G0(z=cncCfg["zSafe"])
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


def buildHinge(baseName):
    #
    wName = "{}{}".format(baseName, "_bottom_C102Asm")
    boxBottomMillC102Asm = living_hingemill_C102()
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
    boxBottomMillC112Asm = living_hingemill_C112()
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
    for asm in (boxBottomMillC102Asm, boxBottomMillC112Asm):
        toolPathMap[asm.name] = asm.genScadToolPath()
    genScadMainCust = partial(genScadMainX,
                              toolPathMap=toolPathMap, )
    wName = "{}{}".format(baseName, "_bottom_all")
    scadName = "{}{}".format(wName, ".scad")
    with open(scadName, 'w') as ofp:
        scadAll = gc.scad.genScad(toolMotions=[], cncCfg=None, name="all", main=genScadMainCust)
        ofp.write(str(scadAll))
    log.info("wrote {}".format(scadName))

    

class LivingHingeShape(gc.shape.BaseShape):
    def _elab(self,
              numPairs):
        toolCutDiameter = self.cncCfg["tool"].cutDiameter
        kerf = toolCutDiameter
        leftCut = 2 * kerf
        pairSize = kerf * 4
        vertices = []
        xOffsets = []
        isCutList = []
        for pairNum in reversed(range(numPairs)):
            xOffsets.append( -(kerf + (2 * pairNum) * kerf))
        for pairNum in range(numPairs):
            xOffsets.append( kerf + (2 * pairNum) * kerf)
        for num, xOffset in enumerate(xOffsets):
            if num % 2 == 0:
                start = (-OUTLINE_SIZE[1] / 2 + leftCut)
                stop = (OUTLINE_SIZE[1] / 2 - leftCut)
                isCutList.append(False)
                vertices.append((xOffset, start))
                isCutList.append(True)
                vertices.append((xOffset, stop, ))
            else:
                start = (-OUTLINE_SIZE[1] / 2)
                stop = (-leftCut)
                isCutList.append(False)
                vertices.append((xOffset, start))
                isCutList.append(True)
                vertices.append((xOffset, stop, ))
                start = leftCut
                stop = (OUTLINE_SIZE[1] / 2)
                isCutList.append(False)
                vertices.append((xOffset, start))
                isCutList.append(True)
                vertices.append((xOffset, stop, ))
        vertices = np.asarray(vertices)
        vertices = self.transforms.doTransform(vertices)
        for v, isCut in zip(vertices, isCutList):
            if isCut:
                self += gc.cmd.G0(z=v[2]+1)
                self += gc.cmd.G1(z=v[2])
                self += gc.cmd.G1(*v)
            else:
                self += gc.cmd.G0(z=self.cncCfg["zSafe"])
                self += gc.cmd.G0(*v[:2])
        # already did transforms on verts, before passing to children so don't transform children!
        self.transforms = gc.hg_coords.TransformList() 

        
class LivingHingeCut(gc.assembly.Assembly):
    def _elab(self,
              numPairs,
              depth, ):
        self += gc.cmd.G0(x=self.center[0], y=self.center[1])
        zStart = self.center[2] + self.cncCfg["zMargin"]
        self += gc.cmd.G0(z=zStart)
        zCutSteps = gc.number.calcZSteps(zStart, -depth, self.cncCfg["defaultDepthPerMillingPass"])
        for zCutStep in zCutSteps:
            self += LivingHingeShape(numPairs=numPairs)
            self.last().translate(z=zCutStep)
        self += gc.cmd.G0(z=zStart)
    
    
def main(argv):
    baseName = "living_hinge"
    buildHinge(baseName)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
