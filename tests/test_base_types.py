import unittest
from gcode_gen import base_types


class TestNamed(unittest.TestCase):
    def test_Named_default_name(self):
        nmd = base_types.Named()
        self.assertIn('<gcode_gen.base_types.Named object at 0x', nmd.name)

    def test_Named_named(self):
        nmd = base_types.Named(name='awesome')
        self.assertEqual(nmd.name, 'awesome')


