'''
machine state
All distance defaults are in millimeters!
'''
from contextlib import contextmanager
from .point import Point
from .tool import Tool

# default homed at x/y=0, but z is indeterminate, estimating 70 mm
DEFAULT_START = Point(0, 0, 70)
DEFAULT_SPINDLE_SPEED = 10000


class State(dict):
    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            raise ValueError('only supports kwargs, not args')
        super().__init__(**kwargs)

    @contextmanager
    def let(self, **kwargs):
        '''temporarily change state based on kwarg key/values.
        for example:
        >>> state = State(feed_rate=40)
        >>> print(state['feed_rate'])
        40
        >>> with state.let(feed_rate=15):
        >>>     print(feed_rate)
        15
        >>> print(state['feed_rate'])
        40
        '''
        stored_state = [(key, self[key]) for key in kwargs.keys()]
        self.update(kwargs)
        yield
        self.update(stored_state)

    @contextmanager
    def excursion(self, nosave=()):
        '''Save state and restore after exiting context block
        for example:
        >>> state = State(feed_rate=40)
        >>> print(state['feed_rate'])
        40
        >>> with state.excursion():
        >>>     state['feed_rate'] = 20
        >>>     print(feed_rate)
        20
        >>> print(state['feed_rate'])
        40
        '''
        assert isinstance(nosave, tuple), isinstance(nosave, list)
        stored_state = []
        for key in self.keys():
            if key not in nosave:
                stored_state.append((key, self[key]))
        yield
        nosave_key_vals = [(key, self[key]) for key in nosave]
        self.clear()
        self.update(nosave_key_vals)
        self.update(stored_state)

    def copy(self):
        return self.__class__(**self)


class CncState(State):
    def __init__(self,
                 tool=None,
                 z_safe=None,
                 spindle_speed=None,
                 depth_per_milling_pass=0.4,
                 depth_per_drilling_pass=1.0,
                 milling_feed_rate=50,
                 drilling_feed_rate=20,
                 feed_rate=None,
                 milling_overlap=0.15,
                 z_margin=0.5,
                 position=None):
        super().__init__()
        self['tool'] = tool
        self['z_safe'] = z_safe
        self['spindle_speed'] = spindle_speed
        self['depth_per_drilling_pass'] = depth_per_drilling_pass
        self['depth_per_milling_pass'] = depth_per_milling_pass
        self['milling_feed_rate'] = milling_feed_rate
        self['drilling_feed_rate'] = drilling_feed_rate
        self['milling_overlap'] = milling_overlap
        self['feed_rate'] = feed_rate
        self['z_margin'] = z_margin
        if position is None:
            self['position'] = DEFAULT_START
        else:
            if not isinstance(position, Point):
                raise TypeError('position must be of type Point')
            self['position'] = position
