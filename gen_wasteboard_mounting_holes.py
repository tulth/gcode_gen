#!/usr/bin/env python
"""Generates gcode for drilling new nomad 883 wasteboard mounting holes"""
import sys
import argparse
import logging

import gcode_gen as gc

log = logging.getLogger()
# log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)
logHandler = logging.StreamHandler(sys.stdout)
log.addHandler(logHandler)

argDoc = "measured wasteboard thickness in mm"

GCODE_OUT_FILE_NAME = "wasteboard_mounting_holes.gcode"
SCAD_OUT_FILE_NAME = "wasteboard_mounting_holes.scad"


class MountingHoleCut(gc.assembly.Assembly):
    def _elab(self,
              wideDiameter, narrowDiameter,
              workpieceThickness,
              shoulderThickness,
              zExtraDepthForLessTearOut=1,
              overlap=None):
        if overlap is None:
            overlap = self.cncCfg["defaultMillingOverlap"]
        self += gc.cmd.G0(z=self.cncCfg["zSafe"])
        self += gc.cmd.G0(self.center[0], self.center[1], )
        self += gc.cut.Cylinder(depth=workpieceThickness - shoulderThickness,
                                diameter=wideDiameter,
                                overlap=overlap).translate(z=workpieceThickness)
        self += gc.cut.Cylinder(depth=shoulderThickness + zExtraDepthForLessTearOut,
                                diameter=narrowDiameter,
                                overlap=overlap,
                                zMargin=0).translate(z=shoulderThickness)
        self += gc.cmd.G0(self.center[0], self.center[1], )
        self += gc.cmd.G0(z=self.cncCfg["zSafe"])

def gen_wasteboard_mounting_holes(wasteboardThickness, scadMain):
    toolDia = (1 / 8) * gc.number.mmPerInch
    comments = []
    comments.append("""Measure NEW wasteboard thickness, for example: 0.506", 0.506", 0.5055", 0.505" = 12.8429 mm""")
    comments.append("""run: {} [{}] """.format(__file__, argDoc))
    comments.append("""start bCNC""")
    comments.append("""Switch bit to {}" flat nose bit""".format(toolDia / gc.number.mmPerInch))
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
        
    bit = gc.tool.Tool(cutDiameter=toolDia)
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         )
    #
    centers = (
        (-9.4, -17.5),
        (-187.2, -17.5),
        (-9.4, -195.3),
        (-187.2, -195.3),
        (-79.25, -106.4),
        )

    asmFile = gc.assembly.FileAsm(name=__doc__, cncCfg=cncCfg, comments=comments, scadMain=scadMain)
    for center in centers:
        asmFile += MountingHoleCut(wideDiameter=10.16,
                                   narrowDiameter=7,
                                   workpieceThickness=wasteboardThickness,
                                   shoulderThickness=2.762).translate(*center)
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

def genScadMain(workpieceThickness):
    scadMainStr = """
module workpiece() {
  translate([-199.9, -208, 0]) 
  """ + "cube([{sx}, {sy}, {sz}]);".format(sx=8 * 25.4, sy=8 * 25.4, sz=workpieceThickness) + """
}
""" + gc.scad.result_main
    return scadMainStr
def main(argv):
    cfg = parseArgs(argv)
    scadMainStr = genScadMain(cfg.WASTEBOARD_THICKNESS_IN_MM)
    topAsm = gen_wasteboard_mounting_holes(cfg.WASTEBOARD_THICKNESS_IN_MM, scadMain=scadMainStr)
    with open(SCAD_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genScad())
    log.info("wrote {}".format(SCAD_OUT_FILE_NAME))
    with open(GCODE_OUT_FILE_NAME, 'w') as ofp:
        ofp.write(topAsm.genGcode())
    log.info("wrote {}".format(GCODE_OUT_FILE_NAME))
    #print(topAsm)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
