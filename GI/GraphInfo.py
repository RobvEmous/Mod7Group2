import MergeAndSearchTools

__author__ = 'Rob'

"""
Stores info about a currently being colored and evaluated graph (for checking isomorphisms)
    _graph_id - the id of the graph the info belongs to (the index within the list of evaluated graphs)
    _max_degree - the highest degree (number of direct neighbors) among all vertices of the graph, this is also the highest color index after initial coloring
    _num_of_colors - the number of unique colors among all colored vertices
    _has_converged - whether the coloring of this graph has converged (does not change after x iterations)
    _has_duplicate_colors - whether the graph contains two vertices with the same color
"""


class GraphInfo():

    def __init__(self, graph_id, has_converged=False):
        self._graph_id = graph_id
        self._has_converged = has_converged
        self._num_of_color_list = []
        self._duplicate_colors = []
        self._changed = True

    def __repr__(self):
        return str(self._graph_id)

    def graph_id(self):
        return self._graph_id

    def num_of_colors(self):
        return len(self._num_of_color_list)

    def max_number(self):
        if self.num_of_colors() == 0:
            return 0
        return self._num_of_color_list[self.num_of_colors() - 1][0]

    def swap_colors(self, color_in, color_out):
        self.increment_num_of_a_color(color_in)
        self.decrement_num_of_a_color(color_out)
        # print(self.__repr__(), 'swap', color_out, '->', color_in)

    def increment_num_of_a_color(self, color):
        index = MergeAndSearchTools.search_pairs(self._num_of_color_list, color, 0, 0)
        if index == -1:
            self._num_of_color_list = MergeAndSearchTools.zip_number(self._num_of_color_list, (color, 1), False)
        else:
            self._num_of_color_list[index] = (color, self._num_of_color_list[index][1] + 1)
        self._changed = True

    def decrement_num_of_a_color(self, color):
        index = MergeAndSearchTools.search_pairs(self._num_of_color_list, color, 0, 0)
        if index != -1:
            if self._num_of_color_list[index][1] == 1:
                self._num_of_color_list.remove(self._num_of_color_list[index])
            else:
                self._num_of_color_list[index] = (color, self._num_of_color_list[index][1] - 1)
        self._changed = True

    def get_num_of_a_color(self, color):
        index = MergeAndSearchTools.search_pairs(self._num_of_color_list, color, 0, 0)
        if index != -1:
            return self._num_of_color_list[index][1]
        else:
            return -1

    def get_all_colors(self):
        return self._num_of_color_list

    def has_converged(self):
        return self._has_converged

    def set_has_converged(self, has_converged):
        self._has_converged = has_converged

    def has_duplicate_colors(self):
        return len(self.get_duplicate_colors()) > 0

    def get_duplicate_colors(self):
        if self._changed:
            self._duplicate_colors = MergeAndSearchTools.sort_pairs(self._num_of_color_list, 1)
            index = MergeAndSearchTools.search_pairs(self._duplicate_colors, 2, 1, 1)
            if index == -1:
                self._duplicate_colors = []
                return self._duplicate_colors
            found = False
            while not found and index > 1:
                if self._duplicate_colors[index - 1][1] == 1:
                    found = True
                    break
                index -= 1
            if found:
                self._duplicate_colors = self._duplicate_colors[index:]
        return self._duplicate_colors
