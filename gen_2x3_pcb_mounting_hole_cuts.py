#!/usr/bin/env python
"""Generates gcode for drilling nomad 883 bottom left alignment pin holes"""
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

GCODE_OUT_FILE_NAME = "2x3_pcb_mounting_hole_cuts.gcode"
SCAD_OUT_FILE_NAME = "2x3_pcb_mounting_hole_cuts.scad"

CENTERS = (((3 - 0.125) * gc.number.mmPerInch, (2 - 0.125) * gc.number.mmPerInch),
           ((0.125) * gc.number.mmPerInch, (0.125) * gc.number.mmPerInch), )

def gen_botleft_alignment_pin_holes():
    comments = []
    comments.append("""Demo, run {} in bCNC""".format(GCODE_OUT_FILE_NAME))
        
    bit = gc.tool.Carbide3D_101()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         )
    #
    DEPTH = (0.060) * gc.number.mmPerInch + 3.175 / 2
    asmFile = gc.assembly.FileAsm(name="botleft", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    for center in CENTERS:
        asm += gc.cut.DrillHole(depth=DEPTH,
                                ).translate(*center)
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
    topAsm = gen_botleft_alignment_pin_holes()
    with open(SCAD_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genScad())
    log.info("wrote {}".format(SCAD_OUT_FILE_NAME))
    with open(GCODE_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genGcode())
    log.info("wrote {}".format(GCODE_OUT_FILE_NAME))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
