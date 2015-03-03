import pdb

from graphIO import writeDOT, loadgraph
from graphinfo import GraphInfo

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

        # first part of the algorithm to color all vertices according to their number of neighbors
        isomorphic = []
        graphs_info = []
        sorted_vertices = [[]]*len(graph_list)
        print('- Initial coloring...')
        for i in range(0, len(graph_list)):
            print(i + 1, 'of', len(graph_list), end=' ')
            graphs_info.append(GraphInfo(i))
            list_of_unique_colors = []
            for j in range(0, len(graph_list[i].V())):
                curr_deg = graph_list[i].V()[j].deg()
                graph_list[i].V()[j].set_colornum(curr_deg)
                if curr_deg > graphs_info[i].max_degree():
                    graphs_info[i].set_max_degree(curr_deg)
                list_of_unique_colors = self.merge_zip(self, list_of_unique_colors, curr_deg, False)
            # sort list of vertices of graph to color
            sorted_vertices[i] = self.merge_sort_color(self, graph_list[i].V())
            if self._save_results:
                writeDOT(graph_list[i], ('Results/colorful_' + str(i) + '.dot'))
            # count number of unique colors
            graphs_info[i].set_num_of_colors(len(list_of_unique_colors))
            print(' max degree =', graphs_info[i].max_degree(), ', # unique colors =', graphs_info[i].num_of_colors())
        # adds all graphs with the same max degree and number of colors to the list of possibly isomorphic graphs
        for i in range(0, len(graphs_info)):
            for j in range(i + 1, len(graphs_info)):
                if graphs_info[i].equal_degree_and_colors(graphs_info[j]):
                    isomorphic.append((i, j))

        # second part of the algorithm to recursively color the vertices according to their neighbors
        print('- Recursive coloring...')
        converged = False
        iteration_counter = 0
        while not converged:
            print('Iteration ', iteration_counter)
            converged = True
            for i in range(0, len(graph_list)):
                if self.binary_search_pairs(self, isomorphic, i, 0) == -1 and self.binary_search_pairs(self, self.merge_sort_pairs(self, isomorphic, 1), i, 1) == -1:
                    print(i + 1, 'of', len(graph_list), ' is not isomorphic and is skipped')
                    continue
                print(i + 1, 'of', len(graph_list), end=' ')
                sortedVerticesCopy, graphs_info[i] = self.color_vertices_by_neighbors(sorted_vertices[i], graphs_info[i])
                if not graphs_info[i].has_converged():
                    converged = False
                # update colors of nodes in graph
                sorted_to_label_vertices = self.merge_sort_label(self, sortedVerticesCopy)
                for j in range(0, len(sorted_to_label_vertices)):
                    graph_list[i].V()[j].set_colornum(sorted_to_label_vertices[graph_list[i].V()[j].get_label()].get_colornum())
                sorted_vertices[i] = self.merge_sort_color(self, graph_list[i].V())
                print(' # unique colors =', graphs_info[i].num_of_colors(), '; converged =', graphs_info[i].has_converged()
                      , '; all colors unique =', not graphs_info[i].has_duplicate_colors())
                writeDOT(graph_list[i], ('Results/colorfulIt_' + str(i) + '_' + str(iteration_counter) + '.dot'))
            # update isomorphism table
            for entry in isomorphic[:]:
                if not graphs_info[entry[0]].equal_degree_and_colors(graphs_info[entry[1]]):
                    isomorphic.remove(entry)
            iteration_counter += 1
        print('Graphs have converged after', iteration_counter, 'iterations.')
        # final part of algorithm to display the found isomorphisms between the graphs
        print('- Matching graphs...')
        isomorphic = self.mergeIsos(isomorphic)
        for entry in isomorphic:
            nonDubs = 0
            hasDubs = False
            for i in range(0, len(entry)):
                if graphs_info[entry[i]].has_duplicate_colors():
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
                    if not graphs_info[entry[i]].has_duplicate_colors():
                        if first:
                            print(entry[i], end='')
                            first = False
                        elif i < len(entry) - 1:
                            print(',', entry[i], end='')
                        else:
                            print(' and', entry[i])

    # Colors the vertices by the color of their neighbors according to three rules:
    #   - if two vertices already have different colors this will remain the same
    #   - if two vertices have the same color but differently colored neighbors, one of them will change color
    #   - if two vertices had the same color, but have now changed color
    #     this color will be the same iff both have equally colored neighbors
    # Should be called iteratively until the coloring is stable (has diverged)
    def color_vertices_by_neighbors(self, sortedVertices, graph_info):
        converged = True
        start_index = 0
        startColor = sortedVertices[0].get_colornum()
        startNbss = self.merge_sort_color(self, sortedVertices[0].nbs())
        colorChangedNeigbors = []
        color_changes = []
        for i in range(1, len(sortedVertices)):
            currNbs = self.merge_sort_color(self, sortedVertices[i].nbs())
            if sortedVertices[i].get_colornum() == startColor:
                # same color: check whether neighbors equal (if not: change color)
                changed = False
                for j in range(0, len(colorChangedNeigbors)):
                    if self.compare_vertices_color(self, colorChangedNeigbors[j][1], currNbs):
                        color_changes.append((sortedVertices[i].get_label(), colorChangedNeigbors[j][0]))
                        changed = True
                        converged = False
                if not changed and not self.compare_vertices_color(self, startNbss, currNbs):
                    graph_info.increment_num_and_degree(1)
                    colorChangedNeigbors.append((graph_info.max_degree(), currNbs))
                    color_changes.append((sortedVertices[i].get_label(), graph_info.max_degree()))
                    converged = False
            else:
                # not same color: new color found, finalize color changes and update start variables
                startColor = sortedVertices[i].get_colornum()
                startNbss = currNbs
                sorted_to_label_vertices = self.merge_sort_label(self, sortedVertices[start_index:i])
                for entry in color_changes:
                    sorted_to_label_vertices[self.binary_search_label(self, sorted_to_label_vertices, entry[0])].set_colornum(entry[1])
                if len(color_changes) > 0:
                    sortedVertices = sortedVertices[0:start_index] + self.merge_sort_color_and_neighbors(self, sortedVertices[start_index:])
                color_changes = []
                colorChangedNeigbors = []
                start_index = i
        sorted_to_label_vertices = self.merge_sort_label(self, sortedVertices[start_index:(len(sortedVertices))])
        for entry in color_changes:
            sorted_to_label_vertices[self.binary_search_label(self, sorted_to_label_vertices, entry[0])].set_colornum(entry[1])
        if converged or graph_info.num_of_colors() >= len(sortedVertices):
            graph_info.set_has_converged(True)
        graph_info.set_has_duplicate_colors(len(sortedVertices) != graph_info.num_of_colors())
        return sortedVertices, graph_info

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

    # Merge sorts the list of vertices sorts to color and sum of neighbor colors :)
    @staticmethod
    def merge_sort_color_and_neighbors(self, vertices):
        if len(vertices) > 1:
            i = int((len(vertices) / 2))
            f = self.merge_sort_color_and_neighbors(self, vertices[:i])
            s = self.merge_sort_color_and_neighbors(self, vertices[i:])
            r = []
            fi = si = 0
            while fi < len(f) and si < len(s):
                if f[fi].get_colornum() > s[si].get_colornum() or (f[fi].get_colornum() == s[si].get_colornum() and f[fi].sum_nbs_colors() > s[si].sum_nbs_colors()):
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
                if f[fi].get_colornum() < s[si].get_colornum(): # TODO should be larger than
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
    def merge_zip(self, number_list, number, allow_dups=True):
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

gifinder = GIFinder(6, 15, True, True)
gifinder.find_isomorphisms()