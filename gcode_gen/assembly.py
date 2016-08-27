from . import cmd
from . import number
from . import hg_coords
from . import scad

class Assembly(object):
    def __init__(self, *args, **kwargs):
        super().__init__()
        baseKwargs = {"name": None, "cncCfg": None }
        self.args = args
        self.kwargs = kwargs
        for argName in baseKwargs:
            if argName in self.kwargs:
                baseKwargs[argName] = self.kwargs[argName]
                del self.kwargs[argName]
        self.transforms = hg_coords.TransformList()
        self._init(**baseKwargs)
        self.elaborated = False

    def _init(self, name=None, cncCfg=None, ):
        if name is None:
            name = self.defaultName()
        self.name = name
        self.cncCfg = cncCfg
        self.children = []
        
    def last(self):
        return self.children[-1]
    
    def defaultName(self):
        return self.__class__.__name__

    def checkType(self, other):
        assert isinstance(other, Assembly) or isinstance(other, cmd.BaseCmd)

    def __iadd__(self, other):
        self.checkType(other)
        if isinstance(other, Assembly):
            other.cncCfg = self.cncCfg
        self.children.append(other)
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

    def genGcode(self):
        self.elab()
        flatAsm = self.getFlattened()
        return flatAsm.genGcode()

    def getScad(self):
        flatAsm = self.getFlattened()
        return flatAsm.genGcode()

    def getFlattened(self):
        flatAsm = FlattenedAssembly()
        flatAsm.append(FlattenedAssemblyEntry("({})".format(self.label)))
        for child in self.children:
            if isinstance(child, Assembly):
                flatAsm.extend(child.getFlattened())
            else:
                flatAsm.append(child)
        return flatAsm

    def elab(self):
        if self.elaborated:
            return
        else:
            self.elaborated = True
            self._elab(*self.args, **self.kwargs)
            for child in self.children:
                if isinstance(child, Assembly):
                    child.transforms.extend(self.transforms)
                    child.elab()

    def expand(self):
        for child in self.children:
            if isinstance(child, Assembly):
                child.expand()
            else:
                if isinstance(child, cmd.SetFeedRate):
                    child.expand(self.cncCfg["lastPosition"], self.cncCfg["lastFeedRate"])
                    self.cncCfg["lastFeedRate"] = child.feedRate
                else:
                    child.expand(self.cncCfg["lastPosition"])
                self.cncCfg["lastPosition"] = child.point

    def genScad(self):
        pointPairList = []
        for child in self.children:
            if isinstance(child, Assembly):
                pointPairList.extend(child.genScad())
            else:
                pointPairList.extend(child.genScad(self.cncCfg["lastPosition"]))
                self.cncCfg["lastPosition"] = child.point
        return pointPairList

    def compress(self):
        childIdxsToPrune = []
        for childIdx, child in enumerate(self.children):
            if isinstance(child, Assembly):
                child.compress()
            else:
                if isinstance(child, cmd.SetFeedRate):
                    child.compress(self.cncCfg["lastPosition"], self.cncCfg["lastFeedRate"])
                    if child.feedRate is not None:
                        self.cncCfg["lastFeedRate"] = child.feedRate
                else:
                    child.compress(self.cncCfg["lastPosition"])
                for idx, val in enumerate(child.point):
                    if val is not None:
                        self.cncCfg["lastPosition"][idx] = val
                if child.isPrunable():
                    childIdxsToPrune.append(childIdx)
        # prune
        self.children = [val for idx, val in enumerate(self.children) if idx not in childIdxsToPrune]

    def _elab(self):
        """Define in subclass, it will get all __init__ args except name, cncCfg"""
        raise NotImpementedError()

    def translate(self, x=0, y=0, z=0):
        self.transforms.translate(x, y, z)
        return self

    def scale(self, sx=1, sy=1, sz=1):
        self.transforms.scale(sx, sy, sz)
        return self
    
    def rotate(self, phi, x=0, y=0, z=1):
        self.transforms.rotate(phi, x, y, z)
        return self

    def customTransform(self, mat, name=None):
        self.transforms.customTransform(mat, name)
        return self


class HeaderAsm(Assembly):

    def _elab(self):
        self += cmd.Home()
        self += cmd.UnitsMillimeters()
        self += cmd.MotionAbsolute()
        self += cmd.SetSpindleSpeed(self.cncCfg["spindleSpeed"])
        self += cmd.ActivateSpindleCW()
        self += cmd.G0(z=self.cncCfg["zSafe"])
        self += cmd.SetFeedRate(self.cncCfg["defaultMillingFeedRate"])
        self += cmd.ArcInXYPlane()


class FooterAsm(Assembly):

    def _elab(self):
        self += cmd.G0(z=self.cncCfg["zSafe"])
        self += cmd.StopSpindle()
        self += cmd.Home()


class FileAsm(Assembly):
    def __init__(self, name=None, cncCfg=None, comments=()):
        super().__init__(name=name, cncCfg=cncCfg, )
        for comment in comments:
            self += cmd.Comment(comment)
        self += HeaderAsm()
        for child in self.children:
            if isinstance(child, Assembly):
                child.elab()

    def elab(self):
        self.cncCfg["lastPosition"] = number.point(0, 0, 70)  # homed at x/y=0, but z is indeterminate, estimating 70
        self.cncCfg["lastFeedRate"] = -1
        super().elab()
        self.expand()
        self.compress()
        
    def _elab(self):
        self += FooterAsm()

    def genScad(self):
        self.elab()
        self.expand()
        self.cncCfg["lastPosition"] = number.point(0, 0, 70)  # homed at x/y=0, but z is indeterminate, estimating 70
        self.cncCfg["lastFeedRate"] = -1
        pointPairList = super().genScad()
        result = scad.genScad(pointPairList)
        self.compress()
        return result


class FlattenedAssemblyEntry(cmd.BaseCmd):
    pass

class FlattenedAssembly(list):

    def genGcode(self):
        strList = []
        for entry in self:
            strList.append(entry.genGcode())
        return "\n".join(strList)

