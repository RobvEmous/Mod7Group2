import pdb

from graphIO import writeDOT, loadgraph
from graphinfo import GraphInfo
from time import time

"""
Class for finding graph isomorphisms
"""


class GIFinder():

    def __init__(self, num_graphs=4, num_vertices=4098, save_results=False, print_non_final_info=False):
        self._num_graphs = num_graphs
        self._num_vertices = num_vertices
        self._save_results = save_results
        self._print_non_final_info = print_non_final_info

    def __repr__(self):
        return str(self._graph_id)

    def find_isomorphisms(self):
        print()
        print('Finding Graph Isomorphisms between', self._num_graphs, 'graphs with', self._num_vertices, 'vertices.')

        # initialisation part of the algorithm which loads the graphs from a file
        print('- Loading graphs...')
        graph_list = loadgraph('Graphs/crefBM_'
                               + str(self._num_graphs) + '_' + str(self._num_vertices) + '.grl', readlist=True)[0]

        sorted_vertices_list, graph_info_list = self.color_all_vertices_by_degree(graph_list)

        isomorphic = []
        # adds all graphs with the same max degree and number of colors to the list of possibly isomorphic graphs
        for i in range(0, len(graph_info_list)):
            for j in range(i + 1, len(graph_info_list)):
                if graph_info_list[i].num_of_colors() == graph_info_list[j].num_of_colors():
                    isomorphic.append((i, j))

        self.color_vertices_by_neighbor_rec(graph_list, sorted_vertices_list, graph_info_list, isomorphic)

        # update colors of nodes in graph
        for i in range(0, len(graph_info_list)):
            sorted_to_label_vertices = self.merge_sort_label(self, sorted_vertices_list[i])
            for j in range(0, len(sorted_to_label_vertices)):
                graph_list[i].V()[j].set_colornum(sorted_to_label_vertices[graph_list[i].V()[j].get_label()].get_colornum())
            sorted_vertices_list[i] = self.merge_sort_color(self, graph_list[i].V())

        # final part of algorithm to display the found isomorphisms between the graphs
        print('- Matching graphs...')
        isomorphic = self.mergeIsos(isomorphic)
        for entry in isomorphic:
            nonDubs = 0
            hasDubs = False
            for i in range(0, len(entry)):
                if graph_info_list[entry[i]].has_duplicate_colors():
                    if not hasDubs:
                        print('Dups found in', entry[i], end='')
                    else:
                        print(',', entry[i], end=' ')
                    hasDubs = True
                else:
                    nonDubs += 1
            if hasDubs:
                print(': problem for now')
            if nonDubs >= 2:
                print('Isomorphism found between: ', end='')
                first = True
                for i in range(0, len(entry)):
                    if not graph_info_list[entry[i]].has_duplicate_colors():
                        if first:
                            print(entry[i], end='')
                            first = False
                        elif i < len(entry) - 1:
                            print(',', entry[i], end='')
                        else:
                            print(' and', entry[i])

    def color_all_vertices_by_degree(self, graph_list):
        print('- Initial coloring...')
        graph_info_list = [None]*len(graph_list)
        sorted_vertices_list = [None]*len(graph_list)
        for i in range(0, len(graph_list)):
            print('Graph', i + 1, 'of', len(graph_list))
            graph_list[i].set_label(i)
            graph_info_list[i] = self.color_vertices_by_degree(graph_list[i])
            # sort list of vertices of graph to color
            sorted_vertices_list[i] = self.merge_sort_color(self, graph_list[i].V())
        return sorted_vertices_list, graph_info_list

    def color_vertices_by_degree(self, graph):
        """
        Colors all vertices according to their number of neighbors (degree)
        :param graph: graph to color the vertices of
        :rtype : list, graphinfo
        :return: vertices_list with vertex coloring by degree (colornum == degree), graph info
        """
        graph_info = GraphInfo(graph.get_label())
        list_of_unique_colors = []
        for j in range(0, len(graph.V())):
            curr_deg = graph.V()[j].deg()
            graph.V()[j].set_colornum(curr_deg)
            graph_info.increment_num_of_a_color(curr_deg)
        if self._save_results:
            writeDOT(graph, ('Results/colorful_' + str(graph.get_label()) + '.dot'))
        return graph_info

    def color_vertices_by_neighbor_rec(self, graph_list, sorted_vertices_list, graph_info_list, isomorphic):
        """
        Recursively colors of the vertices according to their neighbors for all graphs in parallel.
        :param graphs:
        :return:
        """
        print('- Recursive coloring...')
        max_color = graph_info_list[0].max_number()
        iteration_counter = 0
        converged = False
        while not converged:
            for i in range(0, len(sorted_vertices_list[:])):
                if self.binary_search_pairs(self, isomorphic, i, 0) == -1 \
                        and self.binary_search_pairs(self, self.merge_sort_pairs(self, isomorphic, 1), i, 1) == -1:
                    print(i + 1, 'of', len(sorted_vertices_list), ' is not isomorphic and is skipped')
                    sorted_vertices_list[i] = []
                    # TODO fix
            print('Iteration', iteration_counter, end=' ')
            max_color = self.color_vertices_by_neighbors(sorted_vertices_list, graph_info_list, max_color, isomorphic)
            print(max_color)
            converged = True
            for i in range(0, len(sorted_vertices_list)):
                if not graph_info_list[i].has_converged():
                    converged = False
            # re-sort colors of graphs
            for i in range(0, len(sorted_vertices_list)):
                # save current state
                if self._save_results:
                    sorted_to_label_vertices = self.merge_sort_label(self, sorted_vertices_list[i])
                    for j in range(0, len(sorted_to_label_vertices)):
                        graph_list[i].V()[j].set_colornum(sorted_to_label_vertices[graph_list[i].V()[j].get_label()].get_colornum())
                    writeDOT(graph_list[i], ('Results/colorful_it_' + str(iteration_counter) + '_' + str(graph_list[i].get_label()) + '.dot'))
                sorted_vertices_list[i] = self.merge_sort_color(self, graph_list[i].V())

            iteration_counter += 1

    # Colors the vertices by the color of their neighbors according to three rules:
    #   - if two vertices already have different colors this will remain the same
    #   - if two vertices have the same color but differently colored neighbors, one of them will change color
    #   - if two vertices had the same color, but have now changed color
    #     this color will be the same iff both have equally colored neighbors
    # Should be called iteratively until the coloring is stable (has diverged)
    def color_vertices_by_neighbors(self, sorted_vertices_list, graph_info_list, max_color, isomorphic):
        start_color = None
        color_and_neighbors = [] # one list shared by all graphs
        color_changes_within_iteration = [None]*len(sorted_vertices_list)

        former_index_list = [0]*len(sorted_vertices_list)
        current_index_list = [0]*len(sorted_vertices_list)
        converged = [True]*len(sorted_vertices_list)
        done = False
        while not done:
            done = True # if all graphs have checked all their colors this boolean will remain true
            for i in range(0, len(sorted_vertices_list)):
                broke = False
                if current_index_list[i] >= len(sorted_vertices_list[i]):
                    continue
                for j in range(current_index_list[i], len(sorted_vertices_list[i])):
                    done = False
                    if start_color is None:
                        start_color = sorted_vertices_list[i][j].get_colornum()
                        color_and_neighbors = [(start_color, sorted_vertices_list[i][j].nbs())]
                        continue
                    elif sorted_vertices_list[i][j].get_colornum() == start_color:
                        curr_neighbors = sorted_vertices_list[i][j].nbs()
                        # check whether neighbors equal to already defined neighbor-color pair
                        found = False
                        index = self.binary_search_color_and_neighbors(self, color_and_neighbors, curr_neighbors) # binary search for neighbors = lightning-fast :)
                        if index != -1:
                            # neighbors equal to neighbors of already seen vertex: change color to color of this vertex if necessary
                            if sorted_vertices_list[i][j].get_colornum() != color_and_neighbors[index][0]:
                                if color_changes_within_iteration[i] is None:
                                    color_changes_within_iteration[i] = []
                                color_changes_within_iteration[i].append((sorted_vertices_list[i][j].get_label(), color_and_neighbors[index][0]))
                                graph_info_list[i].swap_colors(color_and_neighbors[index][0], sorted_vertices_list[i][j].get_colornum())
                                converged[i] = False
                            found = True
                        if not found:
                            # unique neighbor combination found: hand out new color
                            max_color += 1
                            graph_info_list[i].swap_colors(max_color, sorted_vertices_list[i][j].get_colornum())
                            if color_changes_within_iteration[i] is None:
                                color_changes_within_iteration[i] = []
                            color_changes_within_iteration[i].append((sorted_vertices_list[i][j].get_label(), max_color))
                            color_and_neighbors = self.merge_zip_color_and_neighbors(self, color_and_neighbors, (max_color, curr_neighbors))
                            converged[i] = False
                    else:
                        broke = True
                        break
                # done with current color in this graph: update former and current index
                former_index_list[i] = current_index_list[i]
                if broke:
                    current_index_list[i] = j
                else:
                    current_index_list[i] = j + 1
            if not done:
                # done with current color in all graphs: update isomorphism table, finalize color changes and clear start color
                for entry in isomorphic[:]:
                    if graph_info_list[entry[0]].get_num_of_a_color(start_color) != graph_info_list[entry[1]].get_num_of_a_color(start_color):
                        isomorphic.remove(entry)
                for i in range(0, len(sorted_vertices_list)):
                    if color_changes_within_iteration[i] is not None:
                        sorted_to_label_changes = self.merge_sort_label(self, sorted_vertices_list[i][former_index_list[i]:current_index_list[i]])
                        for entry in color_changes_within_iteration[i]:
                            sorted_to_label_changes[self.binary_search_label(self, sorted_to_label_changes, entry[0])].set_colornum(entry[1])
                start_color = None
                color_changes_within_iteration = [None]*len(sorted_vertices_list)
                color_and_neighbors = []

        for i in range(0, len(sorted_vertices_list)):
            graph_info_list[i].set_has_converged(not graph_info_list[i].has_duplicate_colors() or converged[i])
        return max_color

    # merges 'o.a.' transitive isomorphisms to one list: [0,1],[1,3] -> [0,1,3] and [0,1],[0,3] -> [0,1,3]
    def mergeIsos(self, oldList):
        newList = []
        listIndex = 0
        while len(oldList) > 0:
            root = oldList.pop(0)
            newList.append([root[0], root[1]])
            while len(oldList) > 0 and oldList[0][0] == root[0]:
                newList[listIndex].append(oldList.pop(0)[1])
            len_of_list = len(newList[listIndex])
            i = 0
            added = False
            while i < len_of_list:
                startIndex = self.binary_search_pairs(self, oldList, newList[listIndex][i], 0)
                if startIndex == -1:
                    i += 1
                    continue
                # search forward
                while startIndex < len(oldList) and oldList[startIndex][0] == newList[listIndex][i]:
                    newItem = oldList.pop(startIndex)[1]
                    dub = False
                    for j in range(1, len(newList[listIndex])):
                        if newList[listIndex][j] == newItem:
                            dub = True
                            break
                    if not dub:
                        newList[listIndex].append(newItem)
                        len_of_list += 1
                        added = True
                # search backward
                startIndex -= 1
                while startIndex >= 0 and oldList[startIndex][0] == newList[listIndex][i]:
                    newItem = oldList.pop(startIndex)[1]
                    for j in range(1, len(newList[listIndex])):
                        if newList[listIndex][j] == newItem:
                            dub = True
                            break
                    if not dub:
                        newList[listIndex].append(newItem)
                        len_of_list += 1
                        added = True
                    startIndex -= 1
                    i += 1
            if added:
                newList[listIndex].sort()
            listIndex += 1
        return newList

    # Merge sorts the list of number-tuples to the first or second element (indicated by index)
    @staticmethod
    def merge_sort_pairs(self, list, index):
        if len(list) > 1:
            i = int((len(list) / 2))
            f = self.merge_sort_pairs(self, list[:i], index)
            s = self.merge_sort_pairs(self, list[i:], index)
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
            return list

    # Merge sorts the list of vertices sorts to color
    @staticmethod
    def merge_sort_color(self, vertices):
        if len(vertices) > 1:
            i = int((len(vertices) / 2))
            f = self.merge_sort_color(self, vertices[:i])
            s = self.merge_sort_color(self, vertices[i:])
            r = []
            fi = si = 0
            while fi < len(f) and si < len(s):
                if f[fi].get_colornum() < s[si].get_colornum():
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
            return vertices

    # Merge sorts the list of vertices sorts to label
    @staticmethod
    def merge_sort_label(self, vertices):
        if len(vertices) > 1:
            i = int((len(vertices) / 2))
            f = self.merge_sort_label(self, vertices[:i])
            s = self.merge_sort_label(self, vertices[i:])
            r = []
            fi = si = 0
            while fi < len(f) and si < len(s):
                if f[fi].get_label() < s[si].get_label():
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
            return vertices

    # Adds one item to a sorted list of numbers
    @staticmethod
    def merge_zip_number(self, number_list, number, allow_dups=True):
        result = []
        if len(number_list) == 0:
            result.append(number)
            return result
        fi = self.binary_search_smaller_or_equal(self, number_list, number)
        if fi != -1:
            result += number_list[:(fi + 1)]
        if allow_dups or fi == -1 or number_list[fi] != number:
            result.append(number)
        result += number_list[(fi + 1):]
        return result

    # Adds one item to a sorted list of color, list of neighbors - tuples
    # The list is sorted by the color of all neighbors
    # all lists of neighbors must be sorted to color and of equal length
    @staticmethod
    def merge_zip_color_and_neighbors(self, color_and_neighbors_list, color_and_neighbor):
        result = []
        if len(color_and_neighbors_list) == 0:
            color_and_neighbors_list.append(color_and_neighbor)
            return result
        fi = self.binary_search_smaller_or_equal_color_and_neighbors(self, color_and_neighbors_list, color_and_neighbor)
        if fi != -1:
            result += color_and_neighbors_list[:(fi + 1)]
        result.append(color_and_neighbor)
        result += color_and_neighbors_list[(fi + 1):]
        return result

    # Adds one item to a sorted list of numbers
    @staticmethod
    def binary_search_smaller_or_equal_color_and_neighbors(self, color_and_neighbors_list, color_and_neighbor):
        if len(color_and_neighbors_list) > 0:
            l = 0
            h = len(color_and_neighbors_list) - 1
            comparison = self.compare_colors(color_and_neighbors_list[l][1], color_and_neighbor[1])
            while h - l > 0 and comparison != 0:
                m = int((l + h) / 2)
                if comparison == 0:
                    l = m
                elif comparison == 1:
                    l = m + 1
                else:
                    h = m - 1
                comparison = self.compare_colors(color_and_neighbors_list[l][1], color_and_neighbor[1])
            if comparison != -1:
                return l
            elif l > 0:
                return l - 1
            else:
                return -1
        else:
            return -1

    # Adds one item to a sorted list of numbers
    @staticmethod
    def binary_search_color_and_neighbors(self, color_and_neighbors_list, neighbors):
        if len(color_and_neighbors_list) > 0:
            l = 0
            h = len(color_and_neighbors_list) - 1
            comparison = self.compare_colors(color_and_neighbors_list[l][1], neighbors)
            while h - l > 0 and comparison != 0:
                m = int((l + h) / 2)
                comparison = self.compare_colors(color_and_neighbors_list[m][1], neighbors)
                if comparison == 0:
                    l = m
                elif comparison == 1:
                    l = m + 1
                else:
                    h = m - 1
                comparison = self.compare_colors(color_and_neighbors_list[l][1], neighbors)
            if comparison == 0:
                return l
            else:
                return -1
        else:
            return -1

    def compare_colors(self, list1, list2):
        for i in range(0, len(list1)):
            if list1[i].get_colornum() < list2[i].get_colornum():
                return 1
            elif list1[i].get_colornum() == list2[i].get_colornum():
                continue
            else:
                return -1
        return 0 # it are duplicates

    # Adds one item to a sorted list of numbers
    @staticmethod
    def binary_search_smaller_or_equal(self, number_list, number):
        if len(number_list) > 0:
            l = 0
            h = len(number_list) - 1
            while h - l > 0 and number_list[l] != number:
                m = int((l + h) / 2)
                if number_list[m] == number:
                    l = m
                elif number_list[m] < number:
                    l = m + 1
                else:
                    h = m - 1
            if number_list[l] <= number:
                return l
            elif l > 0:
                return l - 1
            else:
                return -1
        else:
            return -1

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

    # Binary search for label within the list of vertices.
    @staticmethod
    def binary_search_label(self, vertices, a_label):
        l = 0
        h = len(vertices) - 1
        while h - l > 0 and vertices[l].get_label() != a_label:
            m = int((l + h) / 2)
            if vertices[m].get_label() == a_label:
                l = m
            elif vertices[m].get_label() < a_label:
                l = m + 1
            else:
                h = m - 1
        if vertices[l].get_label() == a_label:
            return l
        else:
            return -1

    # Compares colors of the two lists of vertices which should already be sorted to color
    @staticmethod
    def compare_vertices_color(self, l1, l2):
        if len(l1) != len(l2):
            return False
        for i in range(0, len(l1)):
            if l1[i].get_colornum() != l2[i].get_colornum():
                return False
        return True

# Test run of the 49 and 4098 vertex graphs
gifinder1 = GIFinder(4, 4098, True, True)
#gifinder2 = GIFinder(4, 4098, False, True)
t = time()
gifinder1.find_isomorphisms()
print('>> Run time:', time() - t, 'sec.')
#t2 = time()
#gifinder2.find_isomorphisms()
#print(time() - t2)