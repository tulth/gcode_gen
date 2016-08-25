#!/usr/bin/env python
"""Generates gcode for milling serpentine pattern holes"""
import sys
from base import *
import numpy as np

GCODE_OUT_FILE_NAME = "serpentine_pattern_holes.gcode"
SCAD_OUT_FILE_NAME = "serpentine_pattern_holes.scad"

def gen_serpentine_pattern_holes():
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
    yFractXStartEnds = ((0,    0,  10),   # at start height 0, cut from 0 to 1
                        (0.5, -5,  15), # at half  height, cut from -0.5 to 1.5
                        (1.0,  0,  10),   # at end   height, cut from 0 to 1
                        )
    asmFile = asm_file(name=__doc__, cncCfg=cncCfg, comments=comments)
    with asmFile as asm:
        asm += asm_interpolatedSerpentineCut(
            yBottom=0,
            yHeight=10*np.sqrt(3),
            yFractXStartEnds=yFractXStartEnds)
    return asmFile


def parseArgs(argv):
    description = __doc__
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    cfg = parser.parse_args()
    return cfg

def main(argv):
    cfg = parseArgs(argv)
    topAsm = gen_serpentine_pattern_holes()
    with open(SCAD_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genScad())
    log.info("wrote {}".format(SCAD_OUT_FILE_NAME))
    with open(GCODE_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genGcode())
    log.info("wrote {}".format(GCODE_OUT_FILE_NAME))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
