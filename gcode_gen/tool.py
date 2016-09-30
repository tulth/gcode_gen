import numpy as np
from . import number
from . import scad

class Tool(object):
    def __init__(self,
                 cutDiameter,
                 cutHeight,
                 shankDiameter=(1 / 8 * number.mmPerInch),
                 ):
        self.cutDiameter = cutDiameter
        self.shankDiameter = shankDiameter
        self.cutHeight = cutHeight
        
    def getScadModel(self):
        return "cylinder(h={cutHeight}, d={cutDiameter});\n".format(cutHeight=self.cutHeight,
                                                                    cutDiameter=self.cutDiameter)

    def genScadToolPath(self, pointPairList, name):
        result = []
        result.append("module {} () {{".format(scad.makeToolPathName(name)))
        result.append("  module gcp(os) {")
        result.append("    translate(os)")
        result.append(self.getScadModel())
        result.append("  }")
        result.append("")
        result.append("  module gcpp(offset1, offset2) {")
        result.append("    hull () {")
        result.append("      gcp(offset1);")
        result.append("      gcp(offset2);")
        result.append("    }")
        result.append("  }")
        result.append("")
        result.extend(self.genScadToolCoords(pointPairList))
        return result
    
    def genScadToolCoords(self, pointPairList):
        result = []
        result.append("  union() {")
        for pointPair in pointPairList:
            coordStr = "{}, {}".format(*pointPair)
            coordStr = coordStr.replace("(", "[").replace(")", "]")
            result.append("    gcpp({});".format(coordStr))
        result.append("  }")
        result.append("}")
        return result
        
class Carbide3D_101(Tool):
    def __init__(self,
                 ):
        super().__init__(cutDiameter=(1 / 8 * number.mmPerInch),
                         cutHeight=(0.75 * number.mmPerInch),
                         shankDiameter=(1 / 8 * number.mmPerInch),
                         )
        
    def getScadModel(self):
        resultLines = []
        ballNose = "sphere(h={cutHeight}, d={cutDiameter});".format(cutHeight=self.cutHeight-self.cutDiameter,
                                                                      cutDiameter=self.cutDiameter)
        cylinder = "cylinder(h={cutHeight}, d={cutDiameter});".format(cutHeight=self.cutHeight-self.cutDiameter,
                                                                      cutDiameter=self.cutDiameter)
        resultLines.append("translate([0, 0, {}]) {{".format(self.cutDiameter / 2))
        resultLines.append("union() {")
        resultLines.append(ballNose)
        resultLines.append(cylinder)
        resultLines.append("  }")
        resultLines.append("}")
        return "\n".join(resultLines)

    
class Carbide3D_102(Tool):
    def __init__(self,
                 ):
        super().__init__(cutDiameter=(1 / 8 * number.mmPerInch),
                         cutHeight=(0.75 * number.mmPerInch),
                         shankDiameter=(1 / 8 * number.mmPerInch),
                         )
                
class Carbide3D_112(Tool):
    def __init__(self,
                 ):
        super().__init__(cutDiameter=(1 / 16 * number.mmPerInch),
                         cutHeight=(0.25 * number.mmPerInch),
                         shankDiameter=(1 / 8 * number.mmPerInch),
                         )
        
class InventablesPcbDrill_1p2mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cutDiameter=1.2,
                         cutHeight=(0.4 * number.mmPerInch),
                         shankDiameter=(1 / 8 * number.mmPerInch),
                         )
                
class InventablesPcbDrill_1p1mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cutDiameter=1.1,
                         cutHeight=(0.4 * number.mmPerInch),
                         shankDiameter=(1 / 8 * number.mmPerInch),
                         )
                
class InventablesPcbDrill_1p0mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cutDiameter=1,
                         cutHeight=(0.4 * number.mmPerInch),
                         shankDiameter=(1 / 8 * number.mmPerInch),
                         )
                
class InventablesPcbDrill_0p9mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cutDiameter=0.9,
                         cutHeight=(0.4 * number.mmPerInch),
                         shankDiameter=(1 / 8 * number.mmPerInch),
                         )
                
class InventablesPcbDrill_0p8mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cutDiameter=0.8,
                         cutHeight=(0.4 * number.mmPerInch),
                         shankDiameter=(1 / 8 * number.mmPerInch),
                         )
                
class InventablesPcbDrill_0p7mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cutDiameter=0.7,
                         cutHeight=(0.4 * number.mmPerInch),
                         shankDiameter=(1 / 8 * number.mmPerInch),
                         )
                
class InventablesPcbDrill_0p6mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cutDiameter=0.6,
                         cutHeight=(0.4 * number.mmPerInch),
                         shankDiameter=(1 / 8 * number.mmPerInch),
                         )
                
class InventablesPcbDrill_0p5mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cutDiameter=0.5,
                         cutHeight=(0.4 * number.mmPerInch),
                         shankDiameter=(1 / 8 * number.mmPerInch),
                         )
                
class InventablesPcbDrill_0p4mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cutDiameter=0.4,
                         cutHeight=(0.4 * number.mmPerInch),
                         shankDiameter=(1 / 8 * number.mmPerInch),
                         )
                
class InventablesPcbDrill_0p3mm(Tool):
    def __init__(self,
                 ):
        super().__init__(cutDiameter=0.3,
                         cutHeight=(0.4 * number.mmPerInch),
                         shankDiameter=(1 / 8 * number.mmPerInch),
                         )
                
class InventablesPcbMill_P3_3002(Tool):
    def __init__(self,
                 ):
        self.cutAngle = 30 * np.pi / 180
        shankDiameter = (1 / 8 * number.mmPerInch)
        cutHeight = (shankDiameter / 2) / np.tan(self.cutAngle / 2)
        super().__init__(cutDiameter=0.2,
                         cutHeight=cutHeight,
                         shankDiameter=shankDiameter,
                         )
        
                
    def getScadModel(self):
        resultLines = []
        ballNose = "sphere(h={cutHeight}, d={cutDiameter});".format(cutHeight=self.cutHeight-self.cutDiameter,
                                                                      cutDiameter=self.cutDiameter)
        cylinder = "cylinder(h={cutHeight}, d={cutDiameter});".format(cutHeight=self.cutHeight-self.cutDiameter,
                                                                      cutDiameter=self.cutDiameter)
        resultLines.append("translate([0, 0, {}]) {{".format(self.cutDiameter / 2))
        resultLines.append("union() {")
        resultLines.append(ballNose)
        resultLines.append(cylinder)
        resultLines.append("  }")
        resultLines.append("}")
        return "\n".join(resultLines)

