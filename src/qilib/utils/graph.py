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

from typing import Set, Any


class Node:
    def __init__(self, content: Any = None) -> None:
        self.previous_nodes: Set[Node] = set()
        self.next_nodes: Set[Node] = set()
        self.content: Any = content


class Graph:
    def __init__(self) -> None:
        self.start_nodes: Set[Node] = set()
        self.end_nodes: Set[Node] = set()

    def add_node(self, node: Node) -> None:
        self._fix_links(node)

    def add_link(self, from_node: Node, to_node: Node) -> None:
        from_node.next_nodes.add(to_node)
        to_node.previous_nodes.add(from_node)
        self._fix_links(from_node)
        self._fix_links(to_node)

    def _fix_links(self, node: Node) -> None:
        if not node.previous_nodes:
            # No previous nodes. Ensure that this node is reachable from start_nodes
            self.start_nodes.add(node)
        else:
            # There are previous node. This node should not be reachable directly from start_nodes
            self.start_nodes.discard(node)

        if not node.next_nodes:
            # No next nodes. Ensure that this node is reachable from end_nodes.
            self.end_nodes.add(node)
        else:
            # There are next nodes: This node should not be reachable directly from end_nodes
            self.end_nodes.discard(node)
