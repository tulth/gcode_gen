#!/usr/bin/env python
import sys
from base import *

def gen_bot_right_align_holes():
    toolDia = (1 / 8) * mmPerInch
    comments = []
    comments.append('Use {}" ball nose'.format(toolDia / mmPerInch))
    comments.append("Home first!  Zero X and Y at home!")
    comments.append("Zero Z manually using a sheet of paper!")
        
    tool=Tool(cutDiameter=toolDia)
    cncCfg = CncMachineConfig(tool,
                              zSafe=20,
                              )
    #
    holeDepth = 0.35 * mmPerInch
    botRight = (-20, -180)
    centers = []
    offsets = [offsetInches * mmPerInch for offsetInches in (0.5, 1.5, 2.5)]
    for offset in offsets:
        centers.append((botRight[0] + toolDia / 2, botRight[1] + offset))
    for offset in offsets:
        centers.append((botRight[0] - offset, botRight[1] - toolDia / 2))

    asmFile = asm_file(name="Drill bot right align holes in wasteboard", cncCfg=cncCfg, comments=comments)
    with asmFile as asm:
        for center in centers:
            asm += asm_drillHole(center[0], center[1], 
                                 zTop=0, zBottom=-holeDepth, )    
            #asm += cmd_g0(z=cncCfg["zSafe"])
    
    return asmFile


def main(args):
    alignHolesAsm = gen_bot_right_align_holes()
    print(alignHolesAsm.getGcode())
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
