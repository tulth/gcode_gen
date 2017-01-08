#!/usr/bin/env python
import sys
import numpy as np
import gcode_gen as gc
from gcode_gen.debug import DBGP

def doPolyExample(name, vertices, ):
    print("*" * 40)
    print("doPolyExample: {}".format(name))
    poly = gc.poly.Polygon(vertices=vertices, name=name)

    print("{}.vertices: {}".format(poly.name, poly.vertices))
    print("{}.isClockwise: {}".format(poly.name, poly.isClockwise))
    print("{}.isCounterClockwise: {}".format(poly.name, poly.isCounterClockwise))
    print("{}.isConvex: {}".format(poly.name, poly.isConvex))
    print("{}.isSimple: {}".format(poly.name, poly.isSimple))
    poly.plot(figure=True, show=False, color='b')
    
    shrinkPoly = poly.shrinkPoly(1, name="{}Shrink".format(name))
    print("{}.vertices: {}".format(shrinkPoly.name, shrinkPoly.vertices))
    print("{}.isClockwise: {}".format(shrinkPoly.name, shrinkPoly.isClockwise))
    print("{}.isCounterClockwise: {}".format(shrinkPoly.name, shrinkPoly.isCounterClockwise))
    print("{}.isConvex: {}".format(shrinkPoly.name, shrinkPoly.isConvex))
    print("{}.isSimple: {}".format(shrinkPoly.name, shrinkPoly.isSimple))
    shrinkPoly.plot(figure=False, show=False, )

    growPoly = poly.growPoly(0.5, name="{}Grow".format(name))
    print("{}.vertices: {}".format(growPoly.name, growPoly.vertices))
    print("{}.isClockwise: {}".format(growPoly.name, growPoly.isClockwise))
    print("{}.isCounterClockwise: {}".format(growPoly.name, growPoly.isCounterClockwise))
    print("{}.isConvex: {}".format(growPoly.name, growPoly.isConvex))
    print("{}.isSimple: {}".format(growPoly.name, growPoly.isSimple))
    growPoly.plot(figure=False, show=True, color='g')
    print("*" * 40)

def reverseOrientation(vertices):
    result = np.roll(np.asarray(list(reversed(vertices))), 1, axis=0)
    return result

squareVerts = (
    (0, 0),
    (10, 0),
    (10, 10),
    (0, 10),
    )
    
doPolyExample("square", squareVerts)

doPolyExample("squareReversed", reverseOrientation(squareVerts))

squareCollinearVerts = (
    (0, 0),
    (5, 0),
    (10, 0),
    (10, 10),
    (0, 10),
    )
    
doPolyExample("squareCollinear", squareCollinearVerts)

doPolyExample("squareCollinearReversed", reverseOrientation(squareCollinearVerts))

hexagonVerts = np.asarray((
    (-np.sqrt(3)/3,     0, 2.3),       
    (-np.sqrt(3)/6,    -1/2, 2.3),
    ( np.sqrt(3)/6,    -1/2, 2.3),
    ( np.sqrt(3)/3,     0, 2.3),       
    ( np.sqrt(3)/6,     1/2, 2.3),
    (-np.sqrt(3)/6,     1/2, 2.3),
    )) * 8
    
doPolyExample("hexagon", hexagonVerts)

doPolyExample("hexagonReversed", reverseOrientation(hexagonVerts))


squareNotchedVerts = (
    (0, 0),
    (10, 0),
    (10, 4),
    (8, 4),
    (8, 6),
    (10, 6),
    (10, 10),
    (0, 10),
    )
    
doPolyExample("squareNotched", squareNotchedVerts)

doPolyExample("squareNotchedReversed", reverseOrientation(squareNotchedVerts))

# squareBotchedVerts = (
#     (0, 0),
#     (10, 0),
#     (10, 4),
#     (-2, 4),
#     (-2, 6),
#     (10, 6),
#     (10, 10),
#     (0, 10),
#     )

# try:
#     doPolyExample("squareBotched", squareBotchedVerts)
# except gc.poly.PolygonResizeError as err:
#     print(err)

# try:
#     doPolyExample("squareBotchedReversed", reverseOrientation(squareBotchedVerts))
# except gc.poly.PolygonResizeError as err:
#     print(err)


squareSmashedVerts = (
    (0, 0),
    (10, 0),
    (4, 4),
    (0, 10),
    )

try:
    doPolyExample("squareSmashed", squareSmashedVerts)
except gc.poly.PolygonResizeError as err:
    print(err)

try:
    doPolyExample("squareSmashedReversed", reverseOrientation(squareSmashedVerts))
except gc.poly.PolygonResizeError as err:
    print(err)

hexagonSmashedVerts = np.asarray((
    (-np.sqrt(3)/3,     0, 2.3),       
    (-np.sqrt(3)/6,    -1/2, 2.3),
    ( np.sqrt(3)/6,    -1/2, 2.3),
    ( 0,     0, 2.3),       
    ( np.sqrt(3)/6,     1/2, 2.3),
    (-np.sqrt(3)/6,     1/2, 2.3),
    )) * 8
    
doPolyExample("hexagonSmashed", hexagonSmashedVerts)

doPolyExample("hexagonSmashedReversed", reverseOrientation(hexagonSmashedVerts))


xSteps = np.asarray((0.408, 0.408 + 0.57, 0.408 + 0.745, 0.408 + 1.25)) * gc.number.mmPerInch
ySteps = np.asarray((0, 0.195, 0.195 + 0.77, 1.055)) * gc.number.mmPerInch
dr = 3.175 / 2.0
relayVerts = (
    (xSteps[2] + dr, ySteps[0] + dr),
    (xSteps[3] - dr, ySteps[0] + dr),
    (xSteps[3] - dr, ySteps[3] - dr),
    (xSteps[1] + dr, ySteps[3] - dr),
    (xSteps[1] + dr, ySteps[2] - dr),
    (xSteps[1]     , ySteps[2]     ),
    (xSteps[1] + dr, ySteps[2] - dr),
    (xSteps[0] + dr, ySteps[2] - dr),
    (xSteps[0] + dr, ySteps[1] + dr),
    (xSteps[2] + dr, ySteps[1] + dr),
    (xSteps[2]     , ySteps[1]     ),
    (xSteps[2] + dr, ySteps[1] + dr),
    )

try:
    doPolyExample("relay", relayVerts)
except gc.poly.PolygonResizeError as err:
    print(err)

try:
    doPolyExample("relayReversed", reverseOrientation(relayVerts))
except gc.poly.PolygonResizeError as err:
    print(err)

    
