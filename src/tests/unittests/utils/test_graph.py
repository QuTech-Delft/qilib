"""Quantum Inspire library

Copyright 2019 QuTech Delft

qilib is available under the [MIT open-source license](https://opensource.org/licenses/MIT):

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import unittest
from qilib.utils.graph import Graph, Node
from typing import Collection


class TestGraph(unittest.TestCase):
    def assertEmpty(self, obj: Collection):
        self.assertFalse(obj)

    def test_graph_is_initially_empty(self):
        g = Graph()
        self.assertEmpty(g.start_nodes)
        self.assertEmpty(g.end_nodes)

    def test_graph_with_single_node(self):
        g = Graph()
        n = Node()
        g.add_node(n)
        self.assertSetEqual({n}, g.start_nodes)
        self.assertSetEqual({n}, g.end_nodes)
        self.assertEmpty(n.previous_nodes)
        self.assertEmpty(n.next_nodes)

    def test_graph_with_multiple_nodes(self):
        g = Graph()
        n1 = Node()
        n2 = Node()
        n3 = Node()
        n4 = Node()
        n5 = Node()
        g.add_link(n1, n2)
        g.add_link(n1, n3)
        g.add_link(n4, n5)
        g.add_link(n5, n3)
        self.assertSetEqual({n1, n4}, g.start_nodes)
        self.assertSetEqual({n2, n3}, g.end_nodes)
        self.assertEmpty(n1.previous_nodes)
        self.assertSetEqual({n2, n3}, n1.next_nodes)
        self.assertSetEqual({n1}, n2.previous_nodes)
        self.assertEmpty(n2.next_nodes)
        self.assertSetEqual({n1, n5}, n3.previous_nodes)
        self.assertEmpty(n3.next_nodes)
        self.assertEmpty(n4.previous_nodes)
        self.assertSetEqual({n5}, n4.next_nodes)
        self.assertSetEqual({n4}, n5.previous_nodes)
        self.assertSetEqual({n3}, n5.next_nodes)
