#!/bin/env python
import numpy as np
import gcode_gen

# print(gcode_gen.number.calcRSteps(10, 1, 0))

# print(gcode_gen.number.calcFillSteps(0, 10, 1.19, 0))

# print(gcode_gen.number.calcZSteps(0, 10, 1))

# print(gcode_gen.number.calcRSteps(10.16, 3.125, 0.15))
# print(gcode_gen.number.calcRSteps(7, 3.125, 0.15))

# v = np.asarray((
#     (-np.sqrt(3)/3,     0, 2.3),       
#     (-np.sqrt(3)/6,    -1/2, 2.3),
#     ( np.sqrt(3)/6,    -1/2, 2.3),
#     ( np.sqrt(3)/3,     0, 2.3),       
#     ( np.sqrt(3)/6,     1/2, 2.3),
#     (-np.sqrt(3)/6,     1/2, 2.3),
#     ))


# v = gcode_gen.shape.poly_circle_verts(5) * 2
# # v = gcode_gen.shape.HEXAGON * 2
# print(v)
# # print(list(gcode_gen.number.allPlusFirstIter(v)))
# # print(list(gcode_gen.number.verticesToEdgesIter(v)))
# # print(list(gcode_gen.number.edgesToCornersIter(gcode_gen.number.verticesToEdgesIter(v))))
# #print(gcode_gen.vertex.standardizedConvexPolygonVertices(v))
# v = gcode_gen.vertex.standardizedConvexPolygonVertices(v)


# for corner in gcode_gen.vertex.verticesToCornersIter(np.roll(v, 1, axis=0)):
#     gcode_gen.vertex.moveCornerInside(corner, 1)
    
for numVerts in range(3, 17):
    print(numVerts)
    v = gcode_gen.shape.poly_circle_verts(numVerts) * 5
    v = gcode_gen.vertex.standardizedConvexPolygonVertices(v)
    corrections = []
    for corner in gcode_gen.vertex.verticesToCornersIter(np.roll(v, 1, axis=0)):
        corrections.append(gcode_gen.vertex.calcCornerCorrectionVecForToolCutDiameter(corner, 1, False))
    corrections = np.asarray(corrections)
    print(corrections)
    import matplotlib.pyplot as plt
    plt.figure()
    for edge in gcode_gen.vertex.verticesToEdgesIter(v):
        xPoints = [point[0] for point in edge]
        yPoints = [point[1] for point in edge]
        plt.plot(xPoints, yPoints, 'bo-')
    for edge in gcode_gen.vertex.verticesToEdgesIter(v + corrections):
        xPoints = [point[0] for point in edge]
        yPoints = [point[1] for point in edge]
        plt.plot(xPoints, yPoints, 'ro-')
    plt.grid()
    plt.axes().set_aspect('equal')
    plt.show()

    
    
