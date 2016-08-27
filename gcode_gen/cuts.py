from . import assembly
from . import number
from . import cmd

class DrillHole(assembly.Assembly):

    def _elab(self,
              xCenter, yCenter,
              zTop, zBottom,
              name="drillHole",
              plungeRate=None, zMargin=None, ):
        if plungeRate is None:
            plungeRate = self.cncCfg["defaultDrillingFeedRate"]
        if zMargin is None:
            zMargin = self.cncCfg["zMargin"]
        self += cmd.G0(z=self.cncCfg["zSafe"])
        self += cmd.G0(xCenter, yCenter)
        self += cmd.G0(z=zMargin + zTop)
        self += cmd.SetFeedRate(plungeRate)
        self += cmd.G1(z=zBottom)
        self += cmd.G1(z=zTop)
        self += cmd.G0(z=zMargin + zTop)
        self += cmd.G0(z=self.cncCfg["zSafe"])

