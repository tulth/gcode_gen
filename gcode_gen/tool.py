from . import number

class Tool(object):
    def __init__(self,
                 cutDiameter,
                 cutHeight=0.75 * number.mmPerInch, # FIXME, this should not be optional
                 shankDiameter=3.175,
                 ):
        self.cutDiameter = cutDiameter
        self.shankDiameter = shankDiameter
        self.cutHeight = cutHeight
        
    def getScadModel(self):
        return "cylinder(h={cutHeight}, d={cutDiameter});\n".format(cutHeight=self.cutHeight,
                                                                    cutDiameter=self.cutDiameter)
