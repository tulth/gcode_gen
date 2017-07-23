'''basic tree data structure'''
from . import base_types


class Tree(base_types.Named):
    def kwinit(self, name=None, parent=None):
        super().kwinit(name)
        self.parent = parent
        self.children = []

    def check_type(self, other):
        if not isinstance(other, Tree):
            raise TypeError('expected Tree type')

    def append(self, arg):
        self.check_type(arg)
        self.children.append(arg)
        arg.parent = self

    def __iadd__(self, other):
        self.append(other)
        return self

    def __str__(self):
        return self.tree_str()

    def depth_first_walk(self):
        yield MoveDown()
        yield PreOrderVisit(self)
        for child in self.children:
            for walk_step in child.depth_first_walk():
                yield walk_step
        yield PostOrderVisit(self)
        yield MoveUp()

    def tree_str(self):
        indent = 0
        result_lines = []
        for step in self.depth_first_walk():
            if step.is_move:
                if step.is_down:
                    indent += 1
                else:
                    indent -= 1
            elif step.is_visit:
                if step.is_preorder:
                    result_lines.append('{}{}'.format(' ' * (indent - 1), step.visited.name))
        return '\n'.join(result_lines) + '\n'

    def pretty_line(self, prefix):
        return "{}{}".format(self.prefix, self.name, )

    def root_walk(self,):
        yield PreOrderVisit(self)
        if self.parent is not None:
            yield MoveUp()
            for walk_step in self.parent.root_walk():
                yield walk_step
        yield PostOrderVisit(self)


class WalkStep(object):
    def __init__(self,
                 move_not_visit,
                 down_not_up_or_pre_not_post,
                 node=None):
        self.move_not_visit = move_not_visit
        self.down_not_up_or_pre_not_post = down_not_up_or_pre_not_post
        self.node = node

    def __str__(self):
        result = ''
        if self.is_move:
            result += 'move:'
            if self.is_up:
                result += 'up'
            else:
                result += 'down'
        elif self.is_visit:
            result += 'visit:'
            if self.is_preorder:
                result += 'preorder:'
            elif self.is_postorder:
                result += 'postorder:'
            result += self.node.name
        return result

    @property
    def is_move(self):
        return self.move_not_visit

    @property
    def is_visit(self):
        return not self.move_not_visit

    @property
    def is_down(self):
        if not self.is_move:
            raise ValueError('requested up/down on a non move WalkStep')
        return self.down_not_up_or_pre_not_post

    @property
    def is_up(self):
        return not self.is_down

    @property
    def is_visit(self):
        return not self.move_not_visit

    @property
    def is_preorder(self):
        if not self.is_visit:
            raise ValueError('requested pre/post order visit on a non visit WalkStep')
        return self.down_not_up_or_pre_not_post

    @property
    def is_postorder(self):
        return not self.is_preorder

    @property
    def visited(self):
        if not self.is_visit:
            raise ValueError('requested visited node on a non visit WalkStep')
        return self.node


class MoveDown(WalkStep):
    def __init__(self):
        super().__init__(move_not_visit=True,
                         down_not_up_or_pre_not_post=True)


class MoveUp(WalkStep):
    def __init__(self):
        super().__init__(move_not_visit=True,
                         down_not_up_or_pre_not_post=False)


class PreOrderVisit(WalkStep):
    def __init__(self, node):
        super().__init__(move_not_visit=False,
                         down_not_up_or_pre_not_post=True,
                         node=node)


class PostOrderVisit(WalkStep):
    def __init__(self, node):
        super().__init__(move_not_visit=False,
                         down_not_up_or_pre_not_post=False,
                         node=node)


