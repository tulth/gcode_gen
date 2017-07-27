from .tool import Tool
from . import state as st
from . import action
from . import assembly


class Header(assembly.Assembly):
    def get_preorder_actions(self):
        al = action.ActionList()
        al += action.Home(self.state)
        al += action.UnitsMillimeters(self.state)
        al += action.MotionAbsolute(self.state)
        al += action.SetSpindleSpeed(st.DEFAULT_SPINDLE_SPEED, state=self.state)
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
    def __init__(self, name, parent=None, state=None, filename=None):
        super().__init__(name=name, parent=parent, state=state)
        self.filename = filename
        if filename is None:
            self.filename = '{}.gcode'.format(self.name)

    def update_children_preorder(self):
        self += Header()
        self.children.insert(0, self.children.pop())
        self += Footer()

    def update_children_postorder(self):
        self.children = self.children[1:-1]

    def gcode_dumps(self):
        '''dump gcode as a string'''
        gcode_list = self.get_gcode()
        return '\n'.join(map(str, gcode_list))

    def gcode_dump(self, fp):
        '''dump gcode to a file object'''
        gcode_list = self.get_gcode()
        for gcode in gcode_list:
            fp.write('{}\n'.format(str(gcode)))

    def write_gcode_file(self):
        '''dump gcode to a file specified by filename'''
        with open(self.filename, 'w') as file_handle:
            self.gcode_dump(file_handle)


class Project(assembly.Assembly):
    '''Gcode generation project made up of multiple tool passes'''
    def __init__(self, name, parent=None):
        state = st.CncState()
        super().__init__(name=name, parent=parent, state=state)
        self.tool_passes = {}
        self.tools = {}

    def append(self, tool):
        name = '{}_{}'.format(self.name, tool.name)
        state_copy = self.state.copy()
        state_copy['tool'] = tool
        tool_pass = ToolPass(name=name, state=state_copy)
        super().append(tool_pass)

    def write_gcode_files(self, do_print=True):
        '''dump gcode for each toolpass to a file'''
        for tool_pass in self.children:
            if do_print:
                print('Writing file {} ...'.format(tool_pass.filename), end='')
            tool_pass.write_gcode_file()
            if do_print:
                print('done!')


