#!/usr/bin/env python
import sys

header = """$fn=12;

function offset(X=0, Y=0, Z=0) = [X,Y,Z];

function negate(arg) = [-arg[0],-arg[1],-arg[2]];

module gcp(os) {
  translate(os)
    cylinder(h=0.75*25.4, d=0.125*25.4);
    // cylinder(h=0.75*25.4, d=0.05*25.4);
    // cylinder(h=0.75*25.4, d=0.001*25.4);
}
     
module gcpp(offset1, offset2) {
  hull () {
    gcp(offset1);
    gcp(offset2);
  }
}
module main () {
  union() {
"""

footer = """
  }  
}

main();
"""

def genScad(pointPairs):
    moveLines = []
    for pointPair in pointPairs:
        coordStr = "{}, {}".format(*pointPair)
        coordStr = coordStr.replace("(", "[").replace(")", "]")
        moveLines.append("    gcpp({});".format(coordStr))
        
    return "{}{}{}".format(header, "\n".join(moveLines), footer)


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
