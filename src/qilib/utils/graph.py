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
    """A basic node implementation that supports navigation to predecessors and successors.

    Users are expected to inherit from this class and add functionality specific for their application.

    Attribute `previous_nodes` contains the incoming links, i.e. the nodes that are predecessors this node.
    Attribute `next_nodes` contains the outgoing links, i.e. the nodes that are successors of this node.
    When there are no predecessors, this node is considered to be a start node of a graph.
    Similarly, when there are no successors, this node is considered to be an end node of a graph.
    """
    def __init__(self, content: Any = None) -> None:
        self.previous_nodes: Set[Node] = set()
        self.next_nodes: Set[Node] = set()
        self.content: Any = content


class Graph:
    """ A minimalistic graph implementation.

    Users are expected to inherit from this class and add functionality specific for their application.

    Instances of this class can contain nodes of a graph.
    The attribute `start_nodes` contains the graph's start nodes, the attribute `end_nodes` contains the end nodes.
    """
    def __init__(self) -> None:
        self.start_nodes: Set[Node] = set()
        self.end_nodes: Set[Node] = set()

    def add_node(self, node: Node) -> None:
        """ Add a node to the graph.

        If `node` does not have any predecessors, it is added to the graph's start nodes.
        If `node` does not have any successors, it is added to the graph's end nodes.
        """
        self._fix_links(node)

    def add_link(self, from_node: Node, to_node: Node) -> None:
        """ Add a link between two nodes.

        Node `to_node` is added to `from_node`'s successors, and `from_node` is added to `to_node` predecessors.
        When  `from_node` or `to_node` are not yet present in the graph, they are added to
        the graph's `start_nodes` and `end_nodes` respectively.
        """
        from_node.next_nodes.add(to_node)
        to_node.previous_nodes.add(from_node)
        self._fix_links(from_node)
        self._fix_links(to_node)

    def _fix_links(self, node: Node) -> None:
        """ Ensure that the node's links to the graph's `start_nodes` and `end_nodes` is correct."""
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
