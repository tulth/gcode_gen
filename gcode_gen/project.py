# class FileHeaderAsm(AssemblyLeaf):
#     def get_gcode(self):
#         gc = [cmd.Home(),
#               cmd.UnitsMillimeters(),
#               cmd.MotionAbsolute(),
#               cmd.SetSpindleSpeed(self.state['spindle_speed']),
#               cmd.ActivateSpindleCW(),
#               cmd.SetFeedRate(self.state['feed_rate']),
#               ]
#         return gc


# class FileFooterAsm(AssemblyLeaf):
#     def get_gcode(self):
#         gc = [cmd.G0(self.pos.x, self.pos.y, z=self.state['z_safe']),
#               cmd.StopSpindle(),
#               # cmd.Home(),
#               ]
#         return gc

#     def get_points(self):
#         self.pos_mv(z=self.state['z_safe'])
#         return super().get_points()


# class FileAsm(AssemblyRoot):
#     def __init__(self, state, name=None, comments=()):
#         super().__init__(name=name, state=state, )
#         self.comments = comments
#         self += FileHeaderAsm()

#     def _get_gcode_prefix(self):
#         return [cmd.Comment(comment) for comment in self.comments]

