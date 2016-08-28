#!/usr/bin/env python
""""""
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

GCODE_OUT_FILE_NAME = "convex_polgon_cut_demo.gcode"
SCAD_OUT_FILE_NAME = "convex_polgon_cut_demo.scad"


def gen_convex_polgon_cut_demo():
    toolDia = (1 / 8) * gc.number.mmPerInch
    comments = []
    comments.append("""Demo, run {} in bCNC""".format(GCODE_OUT_FILE_NAME))
        
    bit=gc.tool.Tool(cutDiameter=toolDia)
    cncCfg = gc.machine.CncMachineConfig(bit,
                                         zSafe=40,
                                         )
    #
    holeDepth = 0.35 * gc.number.mmPerInch
    botRight = (-20, -180)
    asmFile = gc.assembly.FileAsm(name=__doc__, cncCfg=cncCfg, comments=comments)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    v = gc.shape.HEXAGON * np.sqrt(2) / 2
    print(v)
    asm += gc.cut.ConvexPolygon(vertices=v,
                                depth=0.4,
                                isFilled=True,
                                # isOutline=None,
                                # isOutline=True,
                                isOutline=False,
                                isDogbone=True,
                                ).scale(10, 10)#.translate(2,2)
    asm.last().rotate(-3.14159/4)
    # asm += gc.shape.ConvexPolygonPerimeter(vertices=gc.shape.SQUARE,
    #                                        ).scale(10, 10)
    # asm += gc.shape.ConvexPolygonInsideDogbonePerimeter(vertices=gc.shape.SQUARE,
    #                                               ).scale(10, 10).translate(z=-10)
    return asmFile
    asm += gc.shape.ConvexPolygonPerimeter(vertices=gc.shape.HEXAGON, )
    asm.last().scale(10, 5).rotate(3.14159/4).translate(2, 1)
    asm += gc.shape.ConvexPolygonPerimeter(vertices=gc.shape.EQUILATERAL_TRIANGLE,
                                            ).scale(15, 15).translate(-15, -15)
    asm += gc.shape.ConvexPolygonPerimeter(vertices=gc.shape.poly_circle_verts(64),
                                            ).scale(40, 20)
    asm.last().translate(60, 0)
    asm.rotate(-3.14159/4)
    asm.translate(80, 80)
    asmFile += gc.assembly.Assembly()
    asm = asmFile.last()
    asm += gc.shape.ConvexPolygonFill(vertices=gc.shape.HEXAGON * 10,)
    asm += gc.shape.ConvexPolygonPerimeter(vertices=gc.shape.HEXAGON * 10,)
    # asm.translate(10, 10)
    # asm += gc.cuts.Cylinder(xCenter, yCenter,
    #                          zTop=workpieceThickness,
    #                          zBottom=shoulderThickness,
    #                          diameter=wideDiameter,
    #                          overlap=overlap)
    # asm += gc.cuts.Cylinder(xCenter, yCenter,
    #                          zTop=shoulderThickness,
    #                          zBottom=0-ballPointRadius,
    #                          diameter=narrowDiameter,
    #                          overlap=overlap)
    asm += gc.cmd.G0(z=asm.cncCfg["zSafe"])
    # asmFile.rotate(np.pi/2)
    # print(asmFile)
    # asmFile.elab()
    # print(asmFile)
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
