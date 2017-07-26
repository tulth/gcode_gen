from .tool import Tool
from . import state
from . import action
from . import assembly


# class ToolPass(assembly.Assembly):
#     def kwinit(self, name=None, parent=None, tool=None, state=None):
#         assert state['tool'] is None
#         assert isinstance(tool, Tool)
#         state['tool'] = tool
#         super().kwinit(name, parent, state)


class Header(assembly.TransformableAssemblyLeaf):
    def get_preorder_actions(self):
        al = action.ActionList()
        al += action.Home(self.state)
        al += action.UnitsMillimeters(self.state)
        al += action.MotionAbsolute(self.state)
        al += action.SetSpindleSpeed(state.DEFAULT_SPINDLE_SPEED, state=self.state)
        al += action.ActivateSpindleCW(self.state)
        al += action.SetFeedRate(self.state['milling_feed_rate'], state=self.state)
        return al


class Footer(assembly.TransformableAssembly):
    def kwinit(self, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self += assembly.SafeJog(state=self.state).translate(z=self.state['z_safe'])

    def get_postorder_actions(self):
        al = action.ActionList()
        al += action.StopSpindle(self.state)
        return al


class ToolPass(assembly.TransformableAssembly):
    '''one gcode file, typically used one per tool needed for a project'''
    def kwinit(self, name=None, parent=None, state=None):
        super().kwinit(name=name, parent=parent, state=state)
        self += Header(state=self.state).translate(z=self.state['z_safe'])
        self.save_children = None

    def get_preorder_actions(self):
        if self.save_children is None:
            self.save_children = self.children[:]
        else:
            self.children = self.save_children
        self += Footer(state=self.state)
        return ()
        # actions = super().get_actions()
        # self.children = self.children[:-1]
        # return actions
