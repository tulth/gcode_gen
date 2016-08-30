from . import number
from . import scad

class Tool(object):
    def __init__(self,
                 cutDiameter,
                 cutHeight,
                 shankDiameter=(1 / 8 * 25.4),
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
        super().__init__(cutDiameter=(1 / 8 * 25.4),
                         cutHeight=(0.75 * 25.4),
                         shankDiameter=(1 / 8 * 25.4),
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
        super().__init__(cutDiameter=(1 / 8 * 25.4),
                         cutHeight=(0.75 * 25.4),
                         shankDiameter=(1 / 8 * 25.4),
                         )
                
class Carbide3D_112(Tool):
    def __init__(self,
                 ):
        super().__init__(cutDiameter=(1 / 16 * 25.4),
                         cutHeight=(0.25 * 25.4),
                         shankDiameter=(1 / 8 * 25.4),
                         )
        
