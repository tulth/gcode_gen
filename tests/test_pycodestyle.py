import unittest
import subprocess


class TestStyle(unittest.TestCase):

    def test_style(self):
        subprocess.run(['pycodestyle'], check=True)
