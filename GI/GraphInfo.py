__author__ = 'Rob'

"""
Stores info about a currently being colored and evaluated graph (for checking isomorphisms)
    _graph_id - the id of the graph the info belongs to (the index within the list of evaluated graphs)
    _max_degree - the highest degree (number of direct neighbors) among all vertices of the graph, this is also the highest color index after initial coloring
    _num_of_colors - the number of unique colors among all colored vertices
    _has_diverged - whether the coloring of this graph has diverged (does not change after x iterations)
    _has_duplicate_colors - whether the graph contains two vertices with the same color
"""


class GraphInfo():

    def __init__(self, graph_id, max_degree=0, num_of_colors=0, has_converged=False, has_duplicate_colors=True):
        self._graph_id = graph_id
        self._max_degree = max_degree
        self._num_of_colors = num_of_colors
        self._has_converged = has_converged
        self._has_duplicate_colors = has_duplicate_colors

    def __repr__(self):
        return str(self._graph_id)

    def graph_id(self):
        return self._graph_id

    def max_degree(self):
        return self._max_degree

    def set_max_degree(self, max_degree):
        self._max_degree = max_degree

    def num_of_colors(self):
        return self._num_of_colors

    def set_num_of_colors(self, num_of_colors):
        self._num_of_colors = num_of_colors

    def increment_num_and_degree(self, value):
        self._num_of_colors += value
        self._max_degree += value

    def has_converged(self):
        return self._has_converged

    def set_has_converged(self, has_converged):
        self._has_converged = has_converged

    def has_duplicate_colors(self):
        return self._has_duplicate_colors

    def set_has_duplicate_colors(self, has_duplicate_colors):
        self._has_duplicate_colors = has_duplicate_colors

    def equal_degree_and_colors(self, graph_info_other):
        if graph_info_other.max_degree() != self.max_degree():
            return False
        if graph_info_other.num_of_colors() != self.num_of_colors():
            return False
        return True