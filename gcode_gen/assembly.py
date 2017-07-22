from . import transform
from .point import Point
from .state import State
from . import gcode as cmd


class _BaseAssembly(transform.TransformableMixin):
    '''Private'''
    def __init__(self, name=None):
        super().__init__()
        self.parent = None  # assigned when added as a child
        self.state = None  # assigned at root and root assigns to children when they are added
        self.name = name
        if self.name is None:
            self.name = self.default_name

    def get_gcode(self):
        raise NotImplementedError()

    def get_points(self):
        raise NotImplementedError()

    @property
    def default_name(self):
        return repr(self)

    @property
    def root_transforms(self):
        '''get all assembly transforms stacked all the way to the root'''
        if parent is None:
            return self.transforms
        else:
            return self.parent.root_transforms + self.transforms

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

    @property
    def label(self):
        return '{}:{}'.format(self.__class__.__name__, self.name)


class AssemblyBranch(_BaseAssembly):
    def __init__(self, name=None):
        self.children = []
        super().__init__(name)

    def get_gcode(self):
        result = []
        result.extend(self._get_gcode_prefix())
        for child in self.children:
            result.extend(child.get_gcode())
        result.extend(self._get_gcode_suffix())
        return result

    def get_points(self):
        result = []
        result.extend(self._get_points_prefix())
        for child in self.children:
            result.extend(child.get_points())
        result.extend(self._get_points_suffix())
        return result

    def _get_gcode_prefix(self):
        return []  # define in subclass

    def _get_gcode_suffix(self):
        return []  # define in subclass

    def _get_points_prefix(self):
        return []  # define in subclass

    def _get_points_suffix(self):
        return []  # define in subclass

    def last(self):
        return self.children[-1]

    def append(self, arg):
        self.check_type(arg)
        self.children.append(arg)
        arg.parent = self
        arg.state = self.state

    def check_type(self, other):
        assert isinstance(other, _BaseAssembly)

    def __iadd__(self, other):
        self.append(other)
        return self

    def __str__(self):
        return '\n'.join(self.tree_str())

    def tree_str(self, indent=0):
        str_list = ['{}{}'.format(indent * ' ', self.label)]
        for child in self.children:
            if isinstance(child, Assembly):
                str_list.append(child.tree_str(indent + 2))
            else:
                str_list.append('{}{}'.format((indent + 2) * ' ', child))
        return str_list


class Assembly(AssemblyBranch):
    pass


class AssemblyRoot(AssemblyBranch):
    def __init__(self, name=None, state=None):
        super().__init__(name=name)
        if not isinstance(state, State):
            raise TypeError('state argument must by of type State')
        self.state = state


class AssemblyLeaf(_BaseAssembly):
    def __str__(self):
        return self.label

    def tree_str(self, indent=0):
        return ['{}{}'.format(indent * ' ', self.label)]

    def get_points(self):
        return [self.pos]


class FileHeaderAsm(AssemblyLeaf):
    def get_gcode(self):
        gc = [cmd.Home(),
              cmd.UnitsMillimeters(),
              cmd.MotionAbsolute(),
              cmd.SetSpindleSpeed(self.state['spindle_speed']),
              cmd.ActivateSpindleCW(),
              cmd.SetFeedRate(self.state['feed_rate']),
              ]
        return gc


class FileFooterAsm(AssemblyLeaf):
    def get_gcode(self):
        gc = [cmd.G0(self.pos.x, self.pos.y, z=self.state['z_safe']),
              cmd.StopSpindle(),
              # cmd.Home(),
              ]
        return gc

    def get_points(self):
        self.pos_mv(z=self.state['z_safe'])
        return super().get_points()


class FileAsm(AssemblyRoot):
    def __init__(self, state, name=None, comments=()):
        super().__init__(name=name, state=state, )
        self.comments = comments
        self += FileHeaderAsm()

    def _get_gcode_prefix(self):
        return [cmd.Comment(comment) for comment in self.comments]

