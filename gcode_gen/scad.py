#!/usr/bin/env python
import sys

header = """$fn=12;

module gcpp(offset1, offset2) {
  hull () {
    gcp(offset1);
    gcp(offset2);
  }
}
"""
toolpathStart = """
module toolpath () {
  union() {
"""

toolpath_main = """
module main () {
  toolpath();
}
"""

default_main = toolpath_main

result_main = """
module main () {
  difference() {
    workpiece();
    toolpath(); 
  }
}
"""

footer = """
  }  
}

main();
"""

class genScad(object):
    def __init__(self, pointPairs, cncCfg, main=default_main):
        self.rList = []
        self.rList.append(header)
        self.rList.extend(self.toolCSG(cncCfg["tool"]))
        self.rList.append(main)
        self.rList.append(toolpathStart)
        self.rList.extend(self.toolMotions(pointPairs, cncCfg))
        self.rList.append(footer)

    def __str__(self):
        return "\n".join(self.rList)

    def toolMotions(self, pointPairs, cncCfg):
        result = []
        for pointPair in pointPairs:
            coordStr = "{}, {}".format(*pointPair)
            coordStr = coordStr.replace("(", "[").replace(")", "]")
            result.append("    gcpp({});".format(coordStr))
        return result
        
    def toolCSG(self, tool):
        result = []
        result.append("""module gcp(os) {""")
        result.append("""translate(os)""")
        result.append(tool.getScadModel())
        result.append("""}""")
        return result
        

def demo(argv):
    pointPairs = (((0, 0, 0), (1, 0, 0)),
                  ((1, 0, 0), (1, 1, 0)),
                  ((1, 1, 0), (0, 1, 0)),
                  ((0, 1, 0), (0, 0, 0)),
                  )
    print(gen_scad(pointPairs))
    return 0

if __name__ == '__main__':
    demo(sys.argv)
