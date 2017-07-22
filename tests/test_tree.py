import unittest
from gcode_gen import tree


class TestTree(unittest.TestCase):
    def gen_test_tree(self):
        root = tree.Tree(name='root')
        a = tree.Tree(name='a')
        b = tree.Tree(name='b')
        root += a
        root += b
        c = tree.Tree(name='c')
        d = tree.Tree(name='d')
        e = tree.Tree(name='e')
        f = tree.Tree(name='f')
        g = tree.Tree(name='g')
        b += c
        c += d
        c += e
        c += f
        b += g
        return root

    def test_MoveDown(self):
        actual = str(tree.MoveDown())
        expect = 'move:down'
        self.assertEqual(actual, expect)

    def test_MoveUp(self):
        actual = str(tree.MoveUp())
        expect = 'move:up'
        self.assertEqual(actual, expect)

    def test_PreOrderVisit(self):
        a = tree.Tree(name='a')
        actual = str(tree.PreOrderVisit(a))
        expect = 'visit:preorder:a'
        self.assertEqual(actual, expect)

    def test_PostOrderVisit(self):
        a = tree.Tree(name='a')
        actual = str(tree.PostOrderVisit(a))
        expect = 'visit:postorder:a'
        self.assertEqual(actual, expect)

    def test_depth_first_walk(self):
        root = self.gen_test_tree()
        actual = list(map(str, root.depth_first_walk()))
        expect = ['move:down',
                  'visit:preorder:root',
                  'move:down',
                  'visit:preorder:a',
                  'visit:postorder:a',
                  'move:up',
                  'move:down',
                  'visit:preorder:b',
                  'move:down',
                  'visit:preorder:c',
                  'move:down',
                  'visit:preorder:d',
                  'visit:postorder:d',
                  'move:up',
                  'move:down',
                  'visit:preorder:e',
                  'visit:postorder:e',
                  'move:up',
                  'move:down',
                  'visit:preorder:f',
                  'visit:postorder:f',
                  'move:up',
                  'visit:postorder:c',
                  'move:up',
                  'move:down',
                  'visit:preorder:g',
                  'visit:postorder:g',
                  'move:up',
                  'visit:postorder:b',
                  'move:up',
                  'visit:postorder:root',
                  'move:up',
                  ]
        self.assertEqual(actual, expect)
        for act, exp in zip(actual, expect):
            self.assertEqual(act, exp)

    def test_str(self):
        root = self.gen_test_tree()
        actual = str(root)
        expect = '''root
 a
 b
  c
   d
   e
   f
  g
'''
        self.assertEqual(actual, expect)
