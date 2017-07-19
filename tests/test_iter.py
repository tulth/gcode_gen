import unittest
from gcode_gen import iter_util


class TestIter(unittest.TestCase):

    def test_twice_iter(self):
        actual = tuple(iter_util.twice_iter((1, )))
        expect = (1, 1, )
        self.assertEqual(actual, expect)
        actual = tuple(iter_util.twice_iter((1, 2, 3)))
        expect = (1, 1, 2, 2, 3, 3)
        self.assertEqual(actual, expect)

    def test_pairwise_iter(self):
        actual = tuple(iter_util.pairwise_iter((1, 2, 3)))
        expect = ((1, 2), (2, 3))
        self.assertEqual(actual, expect)
        # a single element gives nothing
        actual = tuple(iter_util.pairwise_iter((1, )))
        expect = ()
        self.assertEqual(actual, expect)

    def test_all_plus_first_iter(self):
        actual = tuple(iter_util.all_plus_first_iter((1, )))
        expect = (1, 1, )
        self.assertEqual(actual, expect)
        actual = tuple(iter_util.all_plus_first_iter((1, 2, 3)))
        expect = (1, 2, 3, 1)
        self.assertEqual(actual, expect)

    def test_loop_pairwise_iter(self):
        actual = tuple(iter_util.loop_pairwise_iter((1, 2, 3)))
        expect = ((1, 2), (2, 3), (3, 1))
        self.assertEqual(actual, expect)
        # a single pair gives first plus last then last plus first!
        actual = tuple(iter_util.loop_pairwise_iter((1, 2)))
        expect = ((1, 2), (2, 1))
        self.assertEqual(actual, expect)
        # a single element gives first, first!
        actual = tuple(iter_util.loop_pairwise_iter((1, )))
        expect = ((1, 1), )
        self.assertEqual(actual, expect)

    def test_serpent_iter(self):
        actual = tuple(iter_util.serpent_iter((1, 0, -1), (2, 3, 4), ))
        expect = (1, 2, 3, 0, -1, 4, )
        self.assertEqual(actual, expect)

    def test_fill_walk_iter(self):
        actual = tuple(iter_util.fill_walk_iter((2, 1, 0), (1, 0, -1), (2, 3, 4), ))
        expect = ((1, 2), (2, 2), (3, 1), (0, 1), (-1, 0), (4, 0), )
        self.assertEqual(actual, expect)
