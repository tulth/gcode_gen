#!/usr/bin/env python
"""Generates gcode for drilling new trapezoid mortise holes"""
import sys
from base import *

argDoc = "measured trapezoid thickness in mm"

GCODE_OUT_FILE_NAME = "trapezoid_mortise_holes.gcode"
SCAD_OUT_FILE_NAME = "trapezoid_mortise_holes.scad"

class asm_filledTrapezoidCut(Assembly):
    """
  ***
 *****
*******
^
botLeft Point

        ->   ***
height  |   *****
        -> *******

 topLength
  |-|
  v v
  ***
 *****
*******
^     ^
|-----|
botLength

    """
    def _elab(self,
              botLeftPoint,
              height,
              topLength,
              botLength,
              overlap=None):
        if overlap is None:
            overlap = self.cncCfg["defaultMillingOverlap"]
        ballPointRadius = self.cncCfg["tool"].cutDiameter / 2
        self += asm_cylinderCut(xCenter, yCenter,
                               zTop=workpieceThickness,
                               zBottom=shoulderThickness,
                               diameter=wideDiameter,
                               overlap=overlap)
        self += asm_cylinderCut(xCenter, yCenter,
                               zTop=shoulderThickness,
                               zBottom=0-ballPointRadius,
                               diameter=narrowDiameter,
                               overlap=overlap)
        self += cmd_g0(z=self.cncCfg["zSafe"])

def gen_trapezoid_mortise_holes(trapezoidThickness):
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
    holeDepth = 0.35 * mmPerInch
    botRight = (-20, -180)
    centers = (
        (0, -0),
        )
    asmFile = asm_file(name=__doc__, cncCfg=cncCfg, comments=comments)
    with asmFile as asm:
        for center in centers:
            cx, cy = center[0], center[1]
            asm += asm_filledTrapezoidCut(cx, cy,
                                       wideDiameter=10.16,
                                       narrowDiameter=7,
                                       workpieceThickness=trapezoidThickness,
                                       shoulderThickness=2.762)
            #asm += cmd_g0(z=cncCfg["zSafe"])
    
    return asmFile


def parseArgs(argv):
    description = __doc__
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    if len(argv) == 1:
        argv.append('-h')

    parser.add_argument('TRAPEZOID_THICKNESS_IN_MM',
                        type=float,
                        help=argDoc,)
    # parser.add_argument('-d', '--debug',
    #                     help='Turn on debug printing.',
    #                     action='store_true',)
    cfg = parser.parse_args()
    return cfg

def main(argv):
    print("NOT FINISHED DO NOT USE")
    sys.exit(1)
    cfg = parseArgs(argv)
    topAsm = gen_trapezoid_mortise_holes(cfg.TRAPEZOID_THICKNESS_IN_MM)
    with open(SCAD_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genScad())
    log.info("wrote {}".format(SCAD_OUT_FILE_NAME))
    with open(GCODE_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genGcode())
    log.info("wrote {}".format(GCODE_OUT_FILE_NAME))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
