#!/bin/env python
"""
lib for gcode gen (and openscad gen).
All numbers represent millimeters.

"""
from __future__ import print_function
import sys
import logging
import argparse
import collections

log = logging.getLogger()
log.setLevel(logging.DEBUG)
logHandler = logging.StreamHandler(sys.stdout)
log.addHandler(logHandler)


class Action(object):
    def __init__(self, cmd, x=None, y=None, z=None, r=None):
        super().__init__()
        self.cmd = cmd
        self.point = point(x, y, z, r)

    def __str__(self):
        return "cmd:{} point:{}".format(self.cmd, self.point)

    def getGcode(self):
        return "{} {}".format(self.cmd, self.point)

class cmd_home(Action):
    """homing cycle"""
    def __init__(self):
        super().__init__("$H")


class cmd_unitsInches(Action):
    """Set system units to inches"""
    def __init__(self):
        super().__init__("G20")


class cmd_unitsMillimeters(Action):
    """Set system units to millimeters"""
    def __init__(self):
        super().__init__("G21")


class cmd_motionAbsolute(Action):
    """Set system to use absolute motion"""
    def __init__(self):
        super().__init__("G90")


class cmd_motionRelative(Action):
    """Set system to use relative motion"""
    def __init__(self):
        raise Exception("Not supported!!")
        # super().__init__("G91")

class cmd_setSpindleSpeed(Action):
    """Set spindle rotation speed"""
    def __init__(self, spindleSpeed):
        super().__init__("S {}".format(spindleSpeed))

class cmd_setFeedRate(Action):
    """set feed rate.  CAUTION: feed rate is system units per minute"""
    def __init__(self, feedRate):
        super().__init__("F {}".format(feedRate))

class cmd_motionAbsolute(Action):
    """Set system to use absolute motion"""
    def __init__(self):
        super().__init__("G90")

class cmd_activateSpindleCW(Action):
    """Activate spindle (clockwise)"""
    def __init__(self, ):
        super().__init__("M3")

class cmd_g0(Action):
    """linear NONcut motion"""
    def __init__(self, x=None, y=None, z=None):
        super().__init__("G0", x, y, z)
    
class cmd_g1(Action):
    """linear CUT motion"""
    def __init__(self, x=None, y=None, z=None):
        super().__init__("G1", x, y, z)
    
class cmd_g2(Action):
    """clockwise arc CUT"""
    def __init__(self, x=None, y=None, z=None, r=None):
        assert r is not None
        super().__init__("G2", x, y, z, r)
    

class Assembly(object):
    def __init__(self, name=None, cncCfg=None, val=None, ):
        super().__init__()
        if name is None:
            name = self.defaultName()
        self.name = name
        self.cncCfg = cncCfg
        if val is not None:
            self.checkType(val)
            self.children = [val]
        else:
            self.children = []

    def defaultName(self):
        return self.__class__.__name__
        
    def checkType(self, other):
        assert isinstance(other, Assembly) or isinstance(other, Action)

    def __iadd__(self, other):
        self.checkType(other)
        self.children.append(other)
        if isinstance(other, Assembly):
            print("isinstance(other, Assembly)")
            other.cncCfg = self.cncCfg
            other.elab()
        return self

    def __str__(self):
        return self.treeStr()

    @property
    def label(self):
        return "Assm:{}".format(self.name)

    def treeStr(self, indent=0):
        strList = ["{}{}".format(indent * " ", self.label)]
        for child in self.children:
            if isinstance(child, Assembly):
                strList.append(child.treeStr(indent + 2))
            else:
                strList.append("{}{}".format((indent + 2) * " ", child))
        return "\n".join(strList)

    def getGcode(self):
        strList = ["({})".format(self.label)]
        for child in self.children:
            strList.append(child.getGcode())
        return "\n".join(strList)

    def elab(self):
        """Define in subclass"""
        pass

class asm_header(Assembly):
    
    def elab(self):
        self += cmd_home()
        self += cmd_unitsMillimeters()
        self += cmd_motionAbsolute()
        # self += cmd_setSpindleSpeed(self.cncCfg["spindleSpeed"])
        self += cmd_setSpindleSpeed(self.cncCfg["spindleSpeed"])
        self += cmd_activateSpindleCW()
        self += cmd_g0(z=self.cncCfg["zSafe"])
        self += cmd_setFeedRate(self.cncCfg["defaultMillingFeedRate"])

        
class asm_file(Assembly):
    def __init__(self, cncCfg, name=None):
         super().__init__(name, cncCfg, )
         self += asm_header()

class asm_drillHole(Assembly):
    
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        if "name" in self.kwargs:
            name = self.kwargs["name"]
            del self.kwargs["name"]
        else:
            name = self.defaultName()
        super().__init__(name=name, cncCfg=None, )
         
    def elab(self):
        self._elab(*self.args, **self.kwargs)
        
    def _elab(self,
              xCenter, yCenter, 
              zTop, zBottom,
              name="drillHole",
              plungeRate=None, zMargin=None):
        if plungeRate is None:
            plungeRate = self.cncCfg["defaultDrillingFeedRate"]
        if zMargin is None:
            zMargin = self.cncCfg["zMargin"]
        self += cmd_g0(self.cncCfg["zSafe"])
        self += cmd_g0(xCenter, yCenter)
        self += cmd_g0(z=zMargin + zTop)
        self += cmd_setFeedRate(plungeRate)
        self += cmd_g1(z=zBottom)
        self += cmd_g1(z=zTop)
        self += cmd_g0(z=zMargin + zTop)
        
class point(list):
    def __init__(self, x=None, y=None, z=None, r=None):
        initArg = []
        for val in (x, y, z, r):
            initArg.append(val)
        super().__init__(initArg)

    def __str__(self):
        retList = []
        for id, val in zip(("X", "Y", "Z", "R"), self):
            if val is not None:
                retList.append("{}{:.5f}".format(id, val))
        return " ".join(retList)


class Tool(object):
    def __init__(self,
                 cutDiameter,
                 shankDiameter=3.175, ):
        self.cutDiameter = cutDiameter
        self.shankDiameter = shankDiameter

class CncMachineConfig(object):
    def __init__(self,
                 tool,
                 zSafe,
                 spindleSpeed=10000,
                 defaultDepthPerMillingPass=0.4,
                 defaultMillingFeedRate=150,
                 defaultDrillingFeedRate=20,
                 zMargin=2):
        assert isinstance(tool, Tool)
        super().__init__()
        self.dict = {}
        self.dict["tool"] = tool
        self.dict["zSafe"] = zSafe
        self.dict["spindleSpeed"] = spindleSpeed
        self.dict["defaultDepthPerMillingPass"] = defaultDepthPerMillingPass
        self.dict["defaultMillingFeedRate"] = defaultMillingFeedRate
        self.dict["defaultDrillingFeedRate"] = defaultDrillingFeedRate
        self.dict["zMargin"] = zMargin

    def __getitem__(self, key):
        return self.dict[key]
    
mmPerInch = 25.4

#def drillbotRightAlignmentHoles():
def demo(argv):
    cfg = parseArgs(argv)
    cncCfg = CncMachineConfig(tool=Tool(cutDiameter=(1 / 8) * mmPerInch),
                              zSafe=50,
                              )
    asm = asm_file(name="demo", cncCfg=cncCfg, )
    asm += asm_drillHole(
        xCenter=10, yCenter=20, 
        zTop=0, zBottom=-30,
        )
    asm += asm_drillHole(
        xCenter=21, yCenter=11, 
        zTop=0, zBottom=-20,
        )
    log.info("*****\n{}\n".format(asm))
    log.info("*****\n{}\n".format(asm.getGcode()))


def parseArgs(argv):
    description = __doc__
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    # if len(argv) == 1:
    #     argv.append('-h')

    parser.add_argument('-d', '--debug',
                        help='Turn on debug printing.',
                        action='store_true',)
    cfg = parser.parse_args()
    return cfg


if __name__ == '__main__':
    demo(sys.argv)
