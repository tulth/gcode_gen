import unittest
from gcode_gen import assembly
from gcode_gen import state
from gcode_gen import tool


class TestAssembly(unittest.TestCase):
    pass


class TestFileAsm(unittest.TestCase):
    def test_basic_file(self):
        st = state.CncState(tool=tool.Carbide3D_101(),
                            z_safe=40)
        asm_file = assembly.FileAsm(st)
        asm_file += assembly.FileFooterAsm()
        print('\n', list(map(lambda x: x.arr, asm_file.get_points())))
        actual = '\n'.join(map(str, asm_file.get_gcode()))
        expect = '''$H
G21
G90
S 10000
M3
F 150
G0 X0.00000 Y0.00000 Z40.00000
M5'''
        self.assertEqual(actual, expect)

    def test_file_comments(self):
        st = state.CncState(tool=tool.Carbide3D_101(),
                            z_safe=40)
        comments = ('hi',
                    'how',
                    'are',
                    'you?', )
        asm_file = assembly.FileAsm(st, comments=comments)
        asm_file += assembly.FileFooterAsm()
        print('\n', asm_file)
        print('\n', list(map(lambda x: str(x.arr), asm_file.get_points())))
        print('\n', '\n'.join(map(str, asm_file.get_gcode())))
        actual = '\n'.join(map(str, asm_file.get_gcode()))
        expect = '''(hi)
(how)
(are)
(you?)
$H
G21
G90
S 10000
M3
F 150
G0 X0.00000 Y0.00000 Z40.00000
M5'''
        self.assertEqual(actual, expect)

