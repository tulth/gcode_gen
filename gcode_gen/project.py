from .tool import Tool
from . import state
from . import action
from . import assembly


class Header(assembly.Assembly):
    def get_preorder_actions(self):
        al = action.ActionList()
        al += action.Home(self.state)
        al += action.UnitsMillimeters(self.state)
        al += action.MotionAbsolute(self.state)
        al += action.SetSpindleSpeed(state.DEFAULT_SPINDLE_SPEED, state=self.state)
        al += action.ActivateSpindleCW(self.state)
        al += action.SetFeedRate(self.state['milling_feed_rate'], state=self.state)
        return al


class Footer(assembly.Assembly):
    def __init__(self, name=None, parent=None, state=None):
        super().__init__(name=name, parent=parent, state=state)

    def update_children_preorder(self):
        self.del_idx = len(self.children)
        self += assembly.SafeJog(state=self.state).translate(z=self.state['z_safe'])

    def get_postorder_actions(self):
        al = action.ActionList()
        al += action.StopSpindle(self.state)
        return al

    def update_children_postorder(self):
        del self.children[self.del_idx]


class ToolPass(assembly.Assembly):
    '''one gcode file, typically used one per tool needed for a project'''
    def update_children_preorder(self):
        self += Header()
        self.children.insert(0, self.children.pop())
        self += Footer()

    def update_children_postorder(self):
        self.children = self.children[1:-1]


class Project(assembly.Assembly):
    '''Gcode generation project made up of multiple tool passes'''
    def update_children_preorder(self):
        self += Header()
        self.children.insert(0, self.children.pop())
        self += Footer()

    def update_children_postorder(self):
        self.children = self.children[1:-1]


