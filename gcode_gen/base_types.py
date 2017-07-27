'''Some helpful base types'''


class Named(object):
    def __init__(self, name=None):
        super().__init__()
        if name is None:
            self.name = self.default_name
        else:
            self.name = name

    @property
    def default_name(self):
        return repr(self)

