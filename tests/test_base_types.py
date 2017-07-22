import unittest
from gcode_gen import base_types


class ExampleInitKwargsOnly(base_types.InitKwargsOnly):
    def kwinit(self, a, b, c):
        pass


class TestInitKwargsOnly(unittest.TestCase):
    def test_InitKwargsOnly_no_args(self):
        ikwo = ExampleInitKwargsOnly(a=1, b=2, c='cat')

    def test_InitKwargsOnly_with_args(self):
        with self.assertRaises(base_types.ArgsUsedError):
            ikwo = ExampleInitKwargsOnly(1, 2, 3)


class TestNamed(unittest.TestCase):
    def test_Named_default_name(self):
        nmd = base_types.Named()
        self.assertIn('<gcode_gen.base_types.Named object at 0x', nmd.name)

    def test_Named_named(self):
        nmd = base_types.Named(name='awesome')
        self.assertEqual(nmd.name, 'awesome')


