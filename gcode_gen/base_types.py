'''Some helpful base types'''


class ArgsUsedError(ValueError):
    pass


class InitKwargsOnly(object):
    def __init__(self, *args, **kwargs):
        super().__init__()
        if args:
            raise ArgsUsedError('only keyword arguments during __init__ are supported, not positional args!')
        self.kwinit(**kwargs)

    def kwinit(self, **kwargs):
        raise NotImplementedError('kwinit must be defined in subclass')


class Named(InitKwargsOnly):
    def kwinit(self, name=None):
        if name is None:
            self.name = self.default_name
        else:
            self.name = name

    @property
    def default_name(self):
        return repr(self)

