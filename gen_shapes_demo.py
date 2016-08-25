#!/usr/bin/env python
"""Generates gcode demoing various shapes"""
import sys
from base import *
import numpy as np

GCODE_OUT_FILE_NAME = "shape_demo.gcode"
SCAD_OUT_FILE_NAME = "shape_demo.scad"

def gen_shapes():
    toolDia = (1 / 8) * mmPerInch
    comments = []
    comments.append("""CAUTIONCAUTIONCAUTION""")
    comments.append("""CAUTIONCAUTIONCAUTION""")
    comments.append("""TEST ONLY!!""")
    comments.append("""CAUTIONCAUTIONCAUTION""")
    comments.append("""CAUTIONCAUTIONCAUTION""")

    tool=Tool(cutDiameter=toolDia)
    cncCfg = CncMachineConfig(tool,
                              zSafe=40,
                              )
    #
    asmFile = asm_file(name=__doc__, cncCfg=cncCfg, comments=comments)
    with asmFile as asm:
        asm += asm_filledConvexPolygon(20*HEXAGON, z=20)
        asm += asm_filledConvexPolygon(insideVertices(20*HEXAGON, 5), z=0)
        # asm += asm_filledConvexPolygon(insideVertices(10*HEXAGON)HEXAGON)
        # print(10*HEXAGON)
        # print(insideVertices(10*HEXAGON), )
        # insideVertices(10*SQUARE)
        # insideVertices(10*EQUILATERAL_TRIANGLE)
        # asm += asm_filledConvexPolygon(SQUARE)
        # asm += asm_filledConvexPolygon(EQUILATERAL_TRIANGLE)
    return asmFile


def parseArgs(argv):
    description = __doc__
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    cfg = parser.parse_args()
    return cfg

def main(argv):
    cfg = parseArgs(argv)
    topAsm = gen_shapes()
    with open(SCAD_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genScad())
    log.info("wrote {}".format(SCAD_OUT_FILE_NAME))
    with open(GCODE_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genGcode())
    log.info("wrote {}".format(GCODE_OUT_FILE_NAME))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
