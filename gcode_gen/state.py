'''
machine state
All distance defaults are in millimeters!
'''
from contextlib import contextmanager
from .point import Point
from .tool import Tool

# default homed at x/y=0, but z is indeterminate, estimating 70 mm
DEFAULT_START = Point(0, 0, 70)


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
    def excursion(self, ):
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
        stored_state = [(key, self[key]) for key in self.keys()]
        yield
        self.clear()
        self.update(stored_state)


class CncState(State):
    def __init__(self,
                 tool,
                 z_safe,
                 spindle_speed=10000,
                 depth_per_milling_pass=0.4,
                 milling_feed_rate=150,
                 drilling_feed_rate=20,
                 feed_rate=None,
                 milling_overlap=0.15,
                 z_margin=0.5,
                 position=None):
        if not isinstance(tool, Tool):
            raise TypeError("tool argument must be of type Tool")
        super().__init__()
        self['tool'] = tool
        self['z_safe'] = z_safe
        self['spindle_speed'] = spindle_speed
        self['depth_per_milling_pass'] = depth_per_milling_pass
        self['milling_feed_rate'] = milling_feed_rate
        self['drilling_feed_rate'] = drilling_feed_rate
        self['milling_overlap'] = milling_overlap
        if feed_rate is None:
            self['feed_rate'] = self['milling_feed_rate']
        else:
            self['feed_rate'] = feed_rate
        self['z_margin'] = z_margin
        if position is None:
            self['position'] = DEFAULT_START
        else:
            if not isinstance(position, Point):
                raise TypeError('position must be of type Point')
            self['position'] = position