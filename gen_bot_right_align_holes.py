#!/usr/bin/env python
"""Generates gcode for drilling nomad 883 bottom right alignment pin holes"""
import sys
import argparse
import logging
import numpy as np
import gcode_gen as gc

log = logging.getLogger()
# log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stdout)
log.addHandler(logHandler)

GCODE_OUT_FILE_NAME = "bot_right_align_holes.gcode"
SCAD_OUT_FILE_NAME = "bot_right_align_holes.scad"


def gen_convex_polgon_cut_demo():
    toolDia = (1 / 8) * gc.number.mmPerInch
    comments = []
    comments.append("""Demo, run {} in bCNC""".format(GCODE_OUT_FILE_NAME))
        
    bit = gc.tool.Carbide3D_101()
    comments.append("tool: {}".format(bit))
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         )
    #
    holeDepth = 0.35 * gc.number.mmPerInch
    botRight = (-20, -180)
    asmFile = gc.assembly.FileAsm(name="bot_right", cncCfg=cncCfg, comments=comments, scadMain=genScadMain)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    botRightOrigin = (-20, -180)
    offsets = [offsetInches * gc.number.mmPerInch for offsetInches in (0.5, 1.5, 2.5)]
    for offset in offsets:
        asm += gc.cut.DrillHole(depth=0.35 * gc.number.mmPerInch,
                                ).translate(x=bit.cutDiameter / 2,
                                            y=offset)
    for offset in offsets:
        asm += gc.cut.DrillHole(depth=0.35 * gc.number.mmPerInch,
                                ).translate(x=-offset,
                                            y=-bit.cutDiameter / 2,)
    asm.translate(*botRightOrigin)
    # asm += gc.shape.ConvexPolygonPerimeter(vertices=gc.shape.SQUARE,
    #                                        ).scale(10, 10)
    # asm += gc.shape.ConvexPolygonInsideDogbonePerimeter(vertices=gc.shape.SQUARE,
    #                                               ).scale(10, 10).translate(z=-10)
    return asmFile


def parseArgs(argv):
    description = __doc__
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    # if len(argv) == 1:
    #     argv.append('-h')

    # parser.add_argument('-d', '--debug',
    #                     help='Turn on debug printing.',
    #                     action='store_true',)
    cfg = parser.parse_args()
    return cfg

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
    cfg = parseArgs(argv)
    topAsm = gen_convex_polgon_cut_demo()
    with open(SCAD_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genScad())
    log.info("wrote {}".format(SCAD_OUT_FILE_NAME))
    with open(GCODE_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genGcode())
    log.info("wrote {}".format(GCODE_OUT_FILE_NAME))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
