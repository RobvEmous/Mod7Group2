import MergeAndSearchTools

__author__ = 'Rob'

"""
Stores info about a currently being colored and evaluated graph (for checking isomorphisms)
    _graph_id - the id of the graph the info belongs to (the index within the list of evaluated graphs)
    _max_number - the highest color number the info holds. A value higher than this will therefore be unique
    _num_of_colors - the number of unique colors among all colored vertices
    _has_converged - whether the coloring of this graph has converged (does not change after x iterations)
    _has_duplicate_colors - whether the graph contains at least two vertices with the same color
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

    def set_graph_id(self, id):
        self._graph_id = id

    def num_of_colors(self):
        return len(self._num_of_color_list)

    def max_number(self):
        if self.num_of_colors() == 0:
            return 0
        return self._num_of_color_list[self.num_of_colors() - 1][0]

    # Adds one to the amount of color_in and decreases the amount of color_out by one.
    def swap_colors(self, color_in, color_out):
        if color_in == color_out:
            print('color-unchanged:', color_in)
        self.increment_num_of_a_color(color_in)
        if not self.decrement_num_of_a_color(color_out):
            print('colorfail:', self._graph_id, color_out, '->', color_in)

    def set_changed(self, changed):
        self._changed = changed

    # When inserting a lot of colors without using the info in the meantime, use this function for increased performance.
    # When done inserting call 'bulk_final_sort()' to be able to normally use the info class.
    def bulk_increment_colors(self, color):
        self._num_of_color_list.append(color)

    def bulk_final_sort(self):
        num_of_color_list_temp = MergeAndSearchTools.sort_number(self._num_of_color_list)
        index = -1
        last_color = -1
        self._num_of_color_list = []
        for entry in num_of_color_list_temp:
            if entry == last_color:
                self._num_of_color_list[index] = \
                    (self._num_of_color_list[index][0], self._num_of_color_list[index][1] + 1)
            else:
                last_color = entry
                index += 1
                self._num_of_color_list.append((entry, 1))

    # Increments the amount of this color, if it was zero, it is added.
    def increment_num_of_a_color(self, color):
        index = MergeAndSearchTools.search_pairs(self._num_of_color_list, color, 0, 0)
        if index == -1:
            self._num_of_color_list = MergeAndSearchTools.zip_number(self._num_of_color_list, (color, 1), False)
        else:
            self._num_of_color_list[index] = (color, self._num_of_color_list[index][1] + 1)
        self._changed = True

    # Decrements the amount of this color and if it was one, it is removed.
    # Returns whether it was there in the first place.
    def decrement_num_of_a_color(self, color):
        index = MergeAndSearchTools.search_pairs(self._num_of_color_list, color, 0, 0)
        if index != -1:
            if self._num_of_color_list[index][1] == 1:
                self._num_of_color_list.remove(self._num_of_color_list[index])
            else:
                self._num_of_color_list[index] = (color, self._num_of_color_list[index][1] - 1)
        else:
            return False
        self._changed = True
        return True

    # Gets the amount of a certain color
    def get_num_of_a_color(self, color):
        index = -1
        try:
            index = MergeAndSearchTools.search_pairs(self._num_of_color_list, color, 0, 0)
        except TypeError:
            print('hoi')
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
                self._changed = False
                return self._duplicate_colors
            found = False
            while not found and index > 0:
                if self._duplicate_colors[index - 1][1] == 1:
                    found = True
                    break
                index -= 1
            if found:
                self._duplicate_colors = self._duplicate_colors[index:]
            self._changed = False
        return self._duplicate_colors

    def get_copy(self):
        new_graph_info = GraphInfo(self.graph_id(), self.has_converged())
        for entry in self._num_of_color_list:
            new_graph_info._num_of_color_list.append((entry[0], entry[1]))
        for entry in self._duplicate_colors:
            new_graph_info._duplicate_colors.append((entry[0], entry[1]))
        new_graph_info._changed = self._changed
        return new_graph_info
