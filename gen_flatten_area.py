#!/usr/bin/env python
"""Generates gcode for flattening nomad 883 wasteboard work area for a 4x6 circuit board blank"""
import sys
import argparse
import logging
import numpy as np
import gcode_gen as gc
import common

log = logging.getLogger()
# log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stdout)
log.addHandler(logHandler)

GCODE_OUT_FILE_NAME = "flatten_area.gcode"
SCAD_OUT_FILE_NAME = "flatten_area.scad"

FLATTEN_DEPTH = 0.2

def gen_flatten_area():
    comments = []
    comments.append("""Demo, run {} in bCNC""".format(GCODE_OUT_FILE_NAME))
        
    bit = gc.tool.Carbide3D_102()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         )
    #
    xWidth, yLength = (6 + 1) * gc.number.mmPerInch, (4 + 1) * gc.number.mmPerInch
    asmFile = gc.assembly.FileAsm(name="flatten", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    asm += gc.cut.RectangleToDepth(depth=FLATTEN_DEPTH,
                                   xWidth=xWidth,
                                   yLength=yLength,
                                   overlap=0.25,
                                   isDogBone=False,
                                   isFilled=True)
    asm.last().translate(xWidth/2, yLength/2)
    asm.last().translate(-12.7, -12.7)
    asm.translate(*common.botLeft)
    return asmFile


def genScadMain(toolPathName):
    result = []
    result.append("module workpiece() {")
    result.append("  translate([-199.9, -208, -12.7]) ")
    result.append("  cube([{sx}, {sy}, {sz}]);".format(sx=8 * 25.4, sy=8 * 25.4, sz=0.5 * 25.4))
    result.append("}")
    result.append("")
    result.extend(gc.scad.result_main(toolPathName))
    return result


def main(argv):
    topAsm = gen_flatten_area()
    with open(SCAD_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genScad())
    log.info("wrote {}".format(SCAD_OUT_FILE_NAME))
    with open(GCODE_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genGcode())
    log.info("wrote {}".format(GCODE_OUT_FILE_NAME))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
