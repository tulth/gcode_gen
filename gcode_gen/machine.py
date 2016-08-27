from .number import point

class Tool(object):
    def __init__(self,
                 cutDiameter,
                 shankDiameter=3.175, ):
        self.cutDiameter = cutDiameter
        self.shankDiameter = shankDiameter

class CncMachineConfig(dict):
    def __init__(self,
                 tool,
                 zSafe,
                 spindleSpeed=10000,
                 defaultDepthPerMillingPass=0.4,
                 defaultMillingFeedRate=150,
                 defaultDrillingFeedRate=20,
                 defaultMillingOverlap=0.15,
                 zMargin=2):
        assert isinstance(tool, Tool)
        super().__init__()
        self["tool"] = tool
        self["zSafe"] = zSafe
        self["spindleSpeed"] = spindleSpeed
        self["defaultDepthPerMillingPass"] = defaultDepthPerMillingPass
        self["defaultMillingFeedRate"] = defaultMillingFeedRate
        self["defaultDrillingFeedRate"] = defaultDrillingFeedRate
        self["defaultMillingOverlap"] = defaultMillingOverlap
        self["zMargin"] = zMargin
        self["lastPosition"] = point(0, 0, 70)  # homed at x/y=0, but z is indeterminate, estimating 70
        self["lastFeedRate"] = -1


