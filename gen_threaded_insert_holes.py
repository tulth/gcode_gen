#!/usr/bin/env python
"""Generates gcode for drilling nomad 883 threaded m3 threaded insert holes"""
import sys
import argparse
import logging
import numpy as np
from functools import partial
import gcode_gen as gc
import common

log = logging.getLogger()
# log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stdout)
log.addHandler(logHandler)


RECESS_DEPTH = 3
FACE_TO_FACE = 4.75
TOTAL_DEPTH = 12.0
INSERT_DEPTH = 5.8

CENTERS = ((0.125 * gc.number.mmPerInch, 0.125 * gc.number.mmPerInch),
           ((6 - 0.125) * gc.number.mmPerInch, 0.125 * gc.number.mmPerInch),
           ((6 - 0.125) * gc.number.mmPerInch, (4 - 0.125) * gc.number.mmPerInch),
           (0.125 * gc.number.mmPerInch, (4 - 0.125) * gc.number.mmPerInch), )
    
class M3ThreadedInsertRoughCut(gc.assembly.Assembly):
    def _elab(self,
              overlap=None):
        if overlap is None:
            overlap = self.cncCfg["defaultMillingOverlap"]
        self += gc.cmd.G0(z=self.cncCfg["zSafe"])
        self += gc.cmd.G0(*self.center[0:2])
        self += gc.cut.HexagonToDepth(depth=RECESS_DEPTH,
                                      faceToFace=FACE_TO_FACE,
                                      isDogBone=False,
                                      overlap=overlap)

        self += gc.cut.Cylinder(depth=INSERT_DEPTH,
                                diameter=4.72,
                                overlap=overlap,
                                zMargin=0).translate(z=-RECESS_DEPTH)
        self += gc.cmd.G0(*self.center[0:2])
        self += gc.cmd.G0(z=self.cncCfg["zSafe"])

class M3ThreadedInsertFineCut(gc.assembly.Assembly):
    def _elab(self,
              overlap=None):
        if overlap is None:
            overlap = self.cncCfg["defaultMillingOverlap"]
        self += gc.cmd.G0(z=self.cncCfg["zSafe"])
        self += gc.cmd.G0(*self.center[0:2])
        self += gc.cut.HexagonToDepth(depth=RECESS_DEPTH,
                                      faceToFace=FACE_TO_FACE + 0.05,
                                      isDogBone=True,
                                      isFilled=False,
                                      overlap=overlap)
        self += gc.cmd.G0(*self.center[0:2])
        self += gc.cmd.G0(z=self.cncCfg["zSafe"])


def doM3ThreadedInsertRoughCut():
    comments = []
    comments.append("""Demo, run {} in bCNC""".format(__name__))

    bit = gc.tool.Carbide3D_102()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         )
    #
    holeDepth = 0.35 * gc.number.mmPerInch
    asmFile = gc.assembly.FileAsm(name="rough", cncCfg=cncCfg, comments=comments, scadMain=None)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    for center in CENTERS:
           asm += M3ThreadedInsertRoughCut().translate(*center)
    asm.translate(*common.botLeft)
    return asmFile

def doM3ThreadedInsertDrillCut():
    comments = []
    comments.append("""Demo, run {} in bCNC""".format(__name__))

    bit = gc.tool.Carbide3D_101()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         )
    #
    holeDepth = 0.35 * gc.number.mmPerInch
    asmFile = gc.assembly.FileAsm(name="drill", cncCfg=cncCfg, comments=comments, scadMain=None)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    for center in CENTERS:
        asm += gc.cut.DrillHole(depth=TOTAL_DEPTH - RECESS_DEPTH - INSERT_DEPTH
                                ).translate(x=center[0],
                                            y=center[1],
                                            z=-RECESS_DEPTH - INSERT_DEPTH)
    asm.translate(*common.botLeft)
    return asmFile


def doM3ThreadedInsertFineCut(scadMain):
    comments = []
    comments.append("""Demo, run {} in bCNC""".format(__name__))

    bit = gc.tool.Carbide3D_112()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         )
    #
    holeDepth = 0.35 * gc.number.mmPerInch
    asmFile = gc.assembly.FileAsm(name="fine", cncCfg=cncCfg, comments=comments, scadMain=scadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    for center in CENTERS:
        asm += M3ThreadedInsertFineCut().translate(*center)
    asm.translate(*common.botLeft)
    return asmFile


def parseArgs(argv):
    description = __doc__
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    cfg = parser.parse_args()
    return cfg

SCAD_WORKPIECE = True
def genScadMainX(toolPathName, roughCutToolPaths, drillCutToolPaths):
    result = []
    result.append("module workpiece() {")
    result.append("  translate([-199.9, -208, -12.7]) ")
    result.append("  cube([{sx}, {sy}, {sz}]);".format(sx=8 * 25.4, sy=8 * 25.4, sz=0.5 * 25.4))
    result.append("}")
    result.append("")
    result.extend(roughCutToolPaths)
    result.extend(drillCutToolPaths)
    result.append("module main () {")
    if SCAD_WORKPIECE:
        result.append("  difference() {")
        result.append("    workpiece();")
    result.append("    union() {")
    result.append("      {}();".format(gc.scad.makeToolPathName("rough")))
    result.append("      {}();".format(gc.scad.makeToolPathName("drill")))
    result.append("      {}();".format(toolPathName))
    if SCAD_WORKPIECE:
        result.append("    }")
    result.append("  }")
    result.append("}")
    return result


def main(argv):
    cfg = parseArgs(argv)
    roughAsm = doM3ThreadedInsertRoughCut()
    gcFileName = "threaded_insert_holes_rough.gcode"
    with open(gcFileName, 'w') as ofp:
        ofp.write(roughAsm.genGcode())
    log.info("wrote {}".format(gcFileName))
    roughCutToolPaths = roughAsm.genScadToolPath()
    #
    drillAsm = doM3ThreadedInsertDrillCut()
    gcFileName = "threaded_insert_holes_drill.gcode"
    with open(gcFileName, 'w') as ofp:
        ofp.write(drillAsm.genGcode())
    log.info("wrote {}".format(gcFileName))
    drillCutToolPaths = drillAsm.genScadToolPath()
    #
    genScadMain = partial(genScadMainX,
                          roughCutToolPaths=roughCutToolPaths,
                          drillCutToolPaths=drillCutToolPaths, )
    fineAsm = doM3ThreadedInsertFineCut(scadMain=genScadMain)
    gcFileName = "threaded_insert_holes_fine.gcode"
    with open(gcFileName, 'w') as ofp:
        ofp.write(fineAsm.genGcode())
    log.info("wrote {}".format(gcFileName))
    SCAD_OUT_FILE_NAME = "threaded_insert_holes.scad"
    with open(SCAD_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(fineAsm.genScad())
    log.info("wrote {}".format(SCAD_OUT_FILE_NAME))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
