from . import assembly

# class Drill(assembly.Assembly):
#     '''drills a hole from z=0 to z=depth
#     use .translate() to set the final x/y/z location of the drill action.
#     '''
#     def __init__(self,
#                  depth,
#                  name="DrillHole",
#                  # plungeRate=None, zMargin=None,
#                  ):
#         # if plungeRate is None:
#         #     plungeRate = self.cncCfg["defaultDrillingFeedRate"]
#         # if zMargin is None:
#         #     zMargin = self.cncCfg["zMargin"]
#         self += SafeJog()
#         self += Drill(z=-depth)
#         # vert = np.asarray(((0,0,zMargin), (0,0,-depth), ), dtype=float)
#         # self.vertices = self.transforms.doTransform(vert)
#         # self += cmd.G0(z=self.cncCfg["zSafe"])
#         # self += cmd.G0(*self.vertices[0][:2])
#         # self += cmd.G0(z=self.vertices[0][2])
#         # originalFeedRate = self.cncCfg["lastFeedRate"]
#         # self += cmd.SetFeedRate(plungeRate)
#         # self += cmd.G1(z=self.vertices[1][2])
#         # self += cmd.G1(z=self.vertices[0][2])
#         # if originalFeedRate is not None and originalFeedRate > 0:
#         #     self += cmd.SetFeedRate(originalFeedRate)
#         # self += cmd.G0(z=self.cncCfg["zSafe"])

# class BaseMotion(TransformableMixin):
#     def __init__(self, x=None, y=None, z=None):
#         super().__init__()
#         self.gc_pnt = GcodeCoordXYZ(x, y, z)


# class Mill(BaseMotion):
#     def get_gcode(self):
#         return (SetFeedRate(self.get_prop('mill feed rate')),
#                 G1(*self.gc_pnt),
#                 )

#     def get_points(self):
#         return (Point(self.gc_pnt), )


# class Drill(BaseMotion):
#     def get_gcode(self):
#         return (SetFeedRate(self.get_prop('drill feed rate')),
#                 G1(*self.gc_pnt),
#                 )

#     def get_points(self):
#         return (Point(self.gc_pnt), )


# class SafeJog(BaseMotion):
#     def get_gcode(self):
#         return (G0(z=self.get_prop('safe z')),
#                 G0(x=self.gc_pnt.x, y=self.gc_pnt.y)),
#                 G0(z=self.get_prop('jog z margin')),
#                 )

#     def get_points(self):
#         return (Point(self.get_points('safe z')),
#                 Point(x=self.gc_pnt.x, y=self.gc_pnt.y),
#                 Point(self.get_prop('jog z margin')),
#                 )



