#!/usr/bin/env python
import sys

header = """$fn=12;
"""

def toolpath_main(toolPathName):
    result = []
    result.append("module main () {")
    result.append("  {}();".format(toolPathName))
    result.append("}")
    return result

default_main = toolpath_main

def result_main(toolPathName):
    result = []
    result.append("module main () {")
    result.append("  difference() {")
    result.append("    workpiece();")
    result.append("    {}();".format(toolPathName))
    result.append("  }")
    result.append("}")
    return result

footer = """

main();
"""

class genScad(object):
    def __init__(self, toolMotions, cncCfg, name, main=default_main):
        toolPathName = makeToolPathName(name)
        self.rList = []
        self.rList.append(header)
        self.rList.extend(main(toolPathName))
        self.rList.extend(toolMotions)
        self.rList.append(footer)

    def __str__(self):
        return "\n".join(self.rList)
        
    def toolCSG(self, tool):
        result = []
        return result
        

def demo(argv):
    pointPairs = (((0, 0, 0), (1, 0, 0)),
                  ((1, 0, 0), (1, 1, 0)),
                  ((1, 1, 0), (0, 1, 0)),
                  ((0, 1, 0), (0, 0, 0)),
                  )
    print(gen_scad(pointPairs))
    return 0

def makeToolPathName(name):
    if name is None:
        return "toolpath"
    return "toolpath_{}".format(name)

if __name__ == '__main__':
    demo(sys.argv)

