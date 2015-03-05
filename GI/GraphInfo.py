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

    def increment_num_of_a_color(self, color):
        index = self.binary_search_pairs(self, self._num_of_color_list, color, 0)
        if index == -1:
            self._num_of_color_list = self.merge_zip_number(self, self._num_of_color_list, (color, 1), 0)
        else:
            self._num_of_color_list[index] = (color, self._num_of_color_list[index][1] + 1)
        self._changed = True

    def decrement_num_of_a_color(self, color):
        index = self.binary_search_pairs(self, self._num_of_color_list, color, 0)
        if index != -1:
            if self._num_of_color_list[index][1] == 1:
                self._num_of_color_list.remove(self._num_of_color_list[index])
            else:
                self._num_of_color_list[index] = (color, self._num_of_color_list[index][1] - 1)
        self._changed = True

    def get_num_of_a_color(self, color):
        index = self.binary_search_pairs(self, self._num_of_color_list, color, 0)
        if index != -1:
            return self._num_of_color_list[index][1]
        else:
            return -1

    def has_converged(self):
        return self._has_converged

    def set_has_converged(self, has_converged):
        self._has_converged = has_converged

    def has_duplicate_colors(self):
        return len(self.get_duplicate_colors()) > 0

    def get_duplicate_colors(self):
        if self._changed:
            self._duplicate_colors = self.merge_sort_pairs(self, self._num_of_color_list, 1)
            index = self.binary_search_bigger_or_equal_pairs(self, self._duplicate_colors, 2, 1)
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

    # Merge sorts the list of number-tuples to the first or second element (indicated by index)
    @staticmethod
    def merge_sort_pairs(self, tuple_list, index):
        if len(tuple_list) > 2:
            i = int((len(tuple_list) / 2))
            f = self.merge_sort_pairs(self, tuple_list[:i], index)
            s = self.merge_sort_pairs(self, tuple_list[i:], index)
            r = []
            fi = si = 0
            while fi < len(f) and si < len(s):
                if f[fi][index] < s[si][index] or f[fi][index] == s[si][index] and f[fi][index == 0] < s[si][index == 0]:
                    r.append(f[fi])
                    fi += 1
                else:
                    r.append(s[si])
                    si += 1
            if fi < len(f):
                r += f[fi:]
            elif si < len(s):
                r += s[si:]
            return r
        else:
            return tuple_list

    # Adds one item to a sorted list of tuples
    @staticmethod
    def merge_zip_number(self, tuple_list, tuple, index):
        result = []
        if len(tuple_list) == 0:
            result.append(tuple)
            return result
        fi = self.binary_search_smaller_or_equal_pairs(self, tuple_list, tuple, index)
        if fi != -1:
            result += tuple_list[:(fi + 1)]
        result.append(tuple)
        result += tuple_list[(fi + 1):]
        return result

    # Binary search for the tuple where the first or second element (indicated by index) is equal to value
    @staticmethod
    def binary_search_pairs(self, tuple_list, value, index):
        if len(tuple_list) > 0:
            l = 0
            h = len(tuple_list) - 1
            while h - l > 0 and tuple_list[l][index] != value:
                m = int((l + h) / 2)
                if tuple_list[m][index] == value:
                    l = m
                elif tuple_list[m][index] < value:
                    l = m + 1
                else:
                    h = m - 1
            if tuple_list[l][index] == value:
                return l
            else:
                return -1
        else:
            return -1

    # Binary search for the tuple where the first or second element (indicated by index) is smaller or equal to value
    @staticmethod
    def binary_search_smaller_or_equal_pairs(self, tuple_list, value, index):
        if len(tuple_list) > 0:
            l = 0
            h = len(tuple_list) - 1
            while h - l > 0 and tuple_list[l][index] != value[index]:
                m = int((l + h) / 2)
                if tuple_list[m][index] == value[index]:
                    l = m
                elif tuple_list[m][index] < value[index]:
                    l = m + 1
                else:
                    h = m - 1
            if tuple_list[l][index] <= value[index]:
                return l
            elif l > 0:
                return l - 1
            else:
                return -1
        else:
            return -1

    # Binary search for the tuple where the first or second element (indicated by index) is smaller or equal to value
    @staticmethod
    def binary_search_bigger_or_equal_pairs(self, tuple_list, value, index):
        if len(tuple_list) > 0:
            l = 0
            h = len(tuple_list) - 1
            while h - l > 0 and tuple_list[l][index] != value:
                m = int((l + h) / 2)
                if tuple_list[m][index] == value:
                    l = m
                elif tuple_list[m][index] < value:
                    l = m + 1
                else:
                    h = m - 1
            if tuple_list[l][index] >= value:
                return l
            elif l < len(tuple_list) - 1:
                return l + 1
            else:
                return -1
        else:
            return -1