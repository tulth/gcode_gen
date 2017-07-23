from functools import partial
from collections import UserList
from collections.abc import MutableSequence
from . import base_types
from . import tree
from . import transform
from .state import CncState
from . import gcode as gc
from . import point as pt


class MotionTree(tree.Tree):
    def kwinit(self, name=None, parent=None, state=None):
        super().kwinit(name, parent)
        self.state = state
        if state is not None:
            if not isinstance(state, CncState):
                raise TypeError('state must be of type cncstate')

    @property
    def pos(self):
        return self.state['position']

    @pos.setter
    def pos(self, arg):
        self.state['position'] = arg

    def pos_mv(self, x=None, y=None, z=None):
        xyz = []
        for new_val, old_val in zip((x, y, z), self.pos.arr):
            val = old_val
            if new_val is not None:
                val = new_val
            xyz.append(val)
        self.pos = Point(*xyz)

    def check_type(self, other):
        assert isinstance(other, MotionTree)

    def append(self, arg):
        super().append(arg)
        # arg.state = self.state
        for walk_step in arg.depth_first_walk():
            if walk_step.is_visit and walk_step.is_preorder:
                node = walk_step.visited
                node.state = self.state

    def last(self):
        return self.children[-1]

    def get_gcode(self):
        return self.get_motion_list().get_gcode()

    @property
    def root_transforms(self):
        '''get transforms stacked all the way to the root'''
        result = transform.TransformList()
        for walk_step in self.root_walk():
            if walk_step.is_visit and walk_step.is_preorder:
                if isinstance(walk_step.visited, TransformableMotionTree):
                    # extend left
                    result[0:0] = walk_step.visited.transforms
        return result

    def get_motion_list(self):
        ml = MotionList()
        skipped_self = False
        for step in self.depth_first_walk():
            if step.is_visit and step.is_preorder:
                if skipped_self:
                    if isinstance(step.visited, TransformableMotionTreeLeaf):
                        ml.extend(step.visited.get_motion_list())
                else:
                    skipped_self = True
        return ml


class TransformableMotionTree(MotionTree, transform.TransformableMixin):
    pass


class TransformableMotionTreeLeaf(TransformableMotionTree):
    def append(self, arg):
        raise NotImplementedError('append is not valid for motion tree leaf')


class MotionPrimitive(object):
    '''Represents a single CNC position or state update
    Note: all motions are transformable'''
    def __init__(self, state=None):
        super().__init__()
        self.state = state

    @property
    def pos(self):
        return self.state['position']

    @pos.setter
    def pos(self, arg):
        self.state['position'] = arg

    def pos_mv(self, x=None, y=None, z=None):
        xyz = []
        for new_val, old_val in zip((x, y, z), self.pos.arr):
            val = old_val
            if new_val is not None:
                val = new_val
            xyz.append(val)
        self.pos = pt.Point(*xyz)

    def get_gcode(self):
        raise NotImplementedError('define gcode generation in base class')

    def get_points(self):
        raise NotImplementedError('define gcode generation in base class')


class GcodeMotionXYZ(MotionPrimitive):
    def __init__(self, gcode_class, x=None, y=None, z=None, state=None):
        super().__init__(state=state)
        old_pos = self.pos
        self.pos_mv(x, y, z)
        self.changes = pt.changes(old_pos, self.pos)
        self.gcode_class = gcode_class

    def get_gcode(self):
        if self.changes:
            return self.gcode_class(**self.changes)
        else:
            return None


class Jog(GcodeMotionXYZ):
    def __init__(self, x=None, y=None, z=None, state=None):
        super().__init__(gcode_class=gc.G0,
                         x=x, y=y, z=z,
                         state=state)


class Cut(GcodeMotionXYZ):
    def __init__(self, x=None, y=None, z=None, state=None):
        super().__init__(gcode_class=gc.G1,
                         x=x, y=y, z=z,
                         state=state)


class MotionList(UserList):
    def append(self, arg):
        self.check_type(arg)
        super().append(arg)

    def extend(self, arg):
        for elem in arg:
            self.check_type(elem)
        super().extend(arg)

    def check_type(self, other):
        if not isinstance(other, MotionPrimitive):
            raise TypeError('expected MotionPrimitive type')

    def __iadd__(self, other):
        'CAUTION: non-list-standard += behavior'
        self.append(other)
        return self

    def get_gcode(self):
        return [elem.get_gcode() for elem in self]


class SafeJog(TransformableMotionTreeLeaf):
    def kwinit(self, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)

    def get_motion_list(self):
        ml = MotionList()
        points = pt.PointList(((0, 0, self.state['z_margin']), ))
        point = pt.PointList(self.root_transforms(points.arr))[0]
        jog = partial(Jog, state=self.state)
        ml += jog(x=self.pos.x, y=self.pos.y, z=self.state['z_safe'])
        ml += jog(x=point.x, y=point.y, z=self.pos.z)
        ml += jog(x=point.x, y=point.y, z=point.z)
        return ml


class UnsafeDrill(TransformableMotionTreeLeaf):
    def kwinit(self, depth, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self.depth = depth

    def get_motion_list(self):
        ml = MotionList()
        points = pt.PointList()
        points.append(pt.Point(0, 0, -self.depth))
        points.append(pt.Point(0, 0, 0))
        points = pt.PointList(self.root_transforms(points.arr))
        cut = partial(Cut, state=self.state)
        ml += cut(*(points[0].arr))
        ml += cut(*(points[1].arr))
        return ml


class Drill(TransformableMotionTree):
    '''drills a hole from z=0 to z=depth
    use .translate() to set the final x/y/z location of the drill action.
    '''
    def kwinit(self, depth, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self += SafeJog()
        self += UnsafeDrill(depth=depth)

#     def get_motion_list(self):
#         motion_list = MotionList()
#         motion_list +=
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



