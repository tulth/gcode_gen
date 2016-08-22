#!/usr/bin/env python
"""Generates gcode for drilling new nomad 883 wasteboard mounting holes"""
import sys
from base import *

argDoc = "measured wasteboard thickness in mm"

GCODE_OUT_FILE_NAME = "wasteboard_mounting_holes.gcode"
SCAD_OUT_FILE_NAME = "wasteboard_mounting_holes.scad"

class asm_mountingHoleCut(Assembly):
    def _elab(self, xCenter, yCenter,
              wideDiameter, narrowDiameter,
              workpieceThickness,
              shoulderThickness,
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

def gen_wasteboard_mounting_holes(wasteboardThickness):
    toolDia = (1 / 8) * mmPerInch
    comments = []
    comments.append("""Measure NEW wasteboard thickness, for example: 0.506", 0.506", 0.5055", 0.505" = 12.8429 mm""")
    comments.append("""run: {} [{}] """.format(__file__, argDoc))
    comments.append("""start bCNC""")
    comments.append("""Switch bit to {}" flat nose bit""".format(toolDia / mmPerInch))
    comments.append("""$H home the machine""")
    comments.append("""Zero X Y""")
    comments.append("""CAUTIONCAUTIONCAUTION""")
    comments.append("""CAUTIONCAUTIONCAUTION""")
    comments.append("""CAUTIONCAUTIONCAUTION""")
    comments.append("""Move to paper-drag-height over OLD wasteboard - not new wasteboard!!""")
    comments.append("""CAUTIONCAUTIONCAUTION""")
    comments.append("""CAUTIONCAUTIONCAUTION""")
    comments.append("""CAUTIONCAUTIONCAUTION""")
    comments.append("""Zero Z""")
    comments.append("""$H home the machine""")
    comments.append("""tape down the new wasteboard""")
    comments.append("""open {} in bCNC""".format(GCODE_OUT_FILE_NAME))
        
    tool=Tool(cutDiameter=toolDia)
    cncCfg = CncMachineConfig(tool,
                              zSafe=40,
                              )
    #
    holeDepth = 0.35 * mmPerInch
    botRight = (-20, -180)
    centers = (
        (-9.4, -17.5),
        (-187.2, -17.5),
        (-9.4, -195.3),
        (-187.2, -195.3),
        (-79.25, -106.4), )

    asmFile = asm_file(name=__doc__, cncCfg=cncCfg, comments=comments)
    with asmFile as asm:
        for center in centers:
            cx, cy = center[0], center[1]
            asm += asm_mountingHoleCut(cx, cy,
                                       wideDiameter=10.16,
                                       narrowDiameter=7,
                                       workpieceThickness=wasteboardThickness,
                                       shoulderThickness=2.762)
            #asm += cmd_g0(z=cncCfg["zSafe"])
    
    return asmFile


def parseArgs(argv):
    description = __doc__
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    if len(argv) == 1:
        argv.append('-h')

    parser.add_argument('WASTEBOARD_THICKNESS_IN_MM',
                        type=float,
                        help=argDoc,)
    # parser.add_argument('-d', '--debug',
    #                     help='Turn on debug printing.',
    #                     action='store_true',)
    cfg = parser.parse_args()
    return cfg

def main(argv):
    cfg = parseArgs(argv)
    topAsm = gen_wasteboard_mounting_holes(cfg.WASTEBOARD_THICKNESS_IN_MM)
    with open(SCAD_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genScad())
    log.info("wrote {}".format(SCAD_OUT_FILE_NAME))
    with open(GCODE_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genGcode())
    log.info("wrote {}".format(GCODE_OUT_FILE_NAME))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
