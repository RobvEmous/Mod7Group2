import MergeAndSearchTools
from graphIO import writeDOT, loadgraph
from graphinfo import GraphInfo
from time import time
import copy

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
        return str(self._num_graphs) + '-' + str(self._num_vertices)

    def graphs_have_isomorphisms(self, graph_list, sorted_vertices_list, graph_info_list, isomorphic):
        if len(isomorphic) == 0:
            return False
        if not graph_info_list[isomorphic[0][0]].has_duplicate_colors():
            return True

        double_colors = graph_info_list[isomorphic[0][0]].get_duplicate_colors()

        indices = [MergeAndSearchTools.search_vertex_color(sorted_vertices_list[isomorphic[0][0]], double_colors[0][0], False)]
        for i in range(0, len(isomorphic)):
            print(isomorphic)
            indices.append(MergeAndSearchTools.search_vertex_color(sorted_vertices_list[isomorphic[i][1]], double_colors[0][0], True))

        max_color = graph_info_list[isomorphic[0][0]].max_number() + 1
        graph_info_list[isomorphic[0][0]].swap_colors(max_color, double_colors[0][0])
        sorted_vertices_list[isomorphic[0][0]][indices[0][0]].set_colornum(max_color)

        for i in range(0, len(indices[0])):
            sorted_vertices_list_copy = copy.deepcopy(sorted_vertices_list)
            graph_info_list_copy = copy.deepcopy(graph_info_list)
            isomorphic_copy = copy.deepcopy(isomorphic)

            for j in range(1, len(indices)):
                graph_info_list_copy[isomorphic[j - 1][1]].swap_colors(max_color, double_colors[0][0])
                sorted_vertices_list_copy[isomorphic[j - 1][1]][indices[j][i]].set_colornum(max_color)

            isomorphic_copy_blow = MergeAndSearchTools.blow_tuples_isomorphisms_all(isomorphic_copy)
            self.color_vertices_by_neighbor_rec(graph_list, sorted_vertices_list_copy, graph_info_list_copy, isomorphic_copy_blow)
            for j in range(0, len(isomorphic_copy_blow)):
                self.graphs_have_isomorphisms(graph_list, sorted_vertices_list_copy, graph_info_list_copy, [isomorphic_copy_blow[j]])
                if len(isomorphic_copy_blow[j][:]) == 0:
                    isomorphic_copy_blow.pop(j)
            if len(isomorphic_copy_blow) == 0:
                return False
            elif len(isomorphic_copy_blow) == 1:
                return True
            else:
                return isomorphic_copy_blow
        return False

    def find_common_double_colors(self, double_colors1, double_colors2):
        for i in range(0, len(double_colors1)):
            for j in range(0, len(double_colors2)):
                if double_colors1[i][0] == double_colors2[j][0]:
                    return double_colors1[i][0]
        return -1

    def find_isomorphisms(self):
        print()
        print('Finding Graph Isomorphisms between', self._num_graphs, 'graphs with', self._num_vertices, 'vertices.')

        # initialisation part of the algorithm which loads the graphs from a file
        print('- Loading graphs...')
        # graph_list = loadgraph('Graphs/crefBM_'
        #
        #                    + str(self._num_graphs) + '_' + str(self._num_vertices) + '.grl', readlist=True)[0]
        graph_list = loadgraph('Graphs/modulesD.grl', readlist=True)[0]

        # part I - initial coloring
        sorted_vertices_list, graph_info_list = self.color_all_vertices_by_degree(graph_list)

        isomorphic = []
        # adds all graphs with the same number of colors to the list of possibly isomorphic graphs
        for i in range(0, len(graph_info_list)):
            for j in range(i + 1, len(graph_info_list)):
                if graph_info_list[i].num_of_colors() == graph_info_list[j].num_of_colors():
                    isomorphic.append((i, j))

        # part II - recursive coloring
        self.color_vertices_by_neighbor_rec(graph_list, sorted_vertices_list, graph_info_list, isomorphic)

        # update colors of nodes in graph
        # IS THIS NECESSARY?
        for i in range(0, len(graph_info_list)):
            sorted_to_label_vertices = MergeAndSearchTools.sort_vertex_label(sorted_vertices_list[i])
            for j in range(0, len(sorted_to_label_vertices)):
                graph_list[i].V()[j].set_colornum(
                    sorted_to_label_vertices[graph_list[i].V()[j].get_label()].get_colornum())

        # recursively get rid of duplicates or remove iso if proven impossible
        isomorphic_zipped = MergeAndSearchTools.zip_tuples_isomorphisms(isomorphic[:])

        for entry in isomorphic_zipped[:]:
            if graph_info_list[entry[0]].has_duplicate_colors():
                print('undecided found - ', entry)
                if not self.graphs_have_isomorphisms(graph_list, sorted_vertices_list, graph_info_list,
                        MergeAndSearchTools.blow_tuples_isomorphisms([entry])):
                    isomorphic_zipped.remove(entry)

        # Part IV all isomorphisms found, print and return results
        print('- Matching graphs...')
        for i in range(0, len(isomorphic_zipped)):
            print('Isomorphism found between: ', end='')
            first = True
            for j in range(0, len(isomorphic_zipped[i])):
                if first:
                    print(isomorphic_zipped[i][j], end='')
                    first = False
                elif j < len(isomorphic_zipped[i]) - 1:
                    print(',', isomorphic_zipped[i][j], end='')
                else:
                    print(' and', isomorphic_zipped[i][j])
        return graph_list, sorted_vertices_list, graph_info_list, isomorphic_zipped

    def color_all_vertices_by_degree(self, graph_list):
        print('- Initial coloring...')
        graph_info_list = [None]*len(graph_list)
        sorted_vertices_list = [None]*len(graph_list)
        for i in range(0, len(graph_list)):
            print('Graph', i, 'of', len(graph_list) - 1)
            graph_list[i].set_label(i)
            graph_info_list[i] = self.color_vertices_by_degree(graph_list[i])
            # sort list of vertices of graph to color
            sorted_vertices_list[i] = MergeAndSearchTools.sort_vertex_color(graph_list[i].V())
        return sorted_vertices_list, graph_info_list

    def color_vertices_by_degree(self, graph):
        """
        Colors all vertices according to their number of neighbors (degree) for one iteration
        :param graph: graph to color the vertices of
        :rtype : list, graph_info
        :return: vertices_list with vertex coloring by degree (color == degree), graph info
        """
        graph_info = GraphInfo(graph.get_label())
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
        :return:
        """
        print('- Recursive coloring...')
        max_color = graph_info_list[0].max_number()
        iteration_counter = 0
        converged = False
        while not converged:
            for i in range(0, len(sorted_vertices_list[:])):
                if MergeAndSearchTools.search_pairs(isomorphic, i, 0, 0) == -1 \
                        and MergeAndSearchTools.search_pairs(
                            MergeAndSearchTools.sort_pairs(isomorphic, 1), i, 1, 0) == -1:
                    print(i, 'of', len(sorted_vertices_list) - 1, ' is not isomorphic and is skipped')
                    sorted_vertices_list[i] = []
            print('Iteration', iteration_counter, end=' ')
            max_color = self.color_vertices_by_neighbors(sorted_vertices_list, graph_info_list, max_color, isomorphic)
            print('-', format((100*(graph_info_list[0].num_of_colors() / self._num_vertices)), '.2f'), '%')
            converged = True
            for i in range(0, len(sorted_vertices_list)):
                if not graph_info_list[i].has_converged():
                    converged = False
            # re-sort colors of graphs
            for i in range(0, len(sorted_vertices_list)):
                # save current state
                if self._save_results:
                    sorted_to_label_vertices = MergeAndSearchTools.sort_vertex_label(sorted_vertices_list[i])
                    for j in range(0, len(sorted_to_label_vertices)):
                        graph_list[i].V()[j].set_colornum(
                            sorted_to_label_vertices[graph_list[i].V()[j].get_label()].get_colornum())
                    writeDOT(graph_list[i], ('Results/colorful_it_' + str(iteration_counter)
                                             + '_' + str(graph_list[i].get_label()) + '.dot'))
                sorted_vertices_list[i] = MergeAndSearchTools.sort_vertex_color(sorted_vertices_list[i])

            iteration_counter += 1

    # Colors the vertices by the color of their neighbors according to three rules:
    #   - if two vertices already have different colors this will remain the same
    #   - if two vertices have the same color but differently colored neighbors, one of them will change color
    #   - if two vertices had the same color, but have now changed color
    #     this color will be the same iff both have equally colored neighbors
    # Should be called iteratively until the coloring is stable (has diverged)
    @staticmethod
    def color_vertices_by_neighbors(sorted_vertices_list, graph_info_list, max_color, isomorphic):
        start_color = None
        color_and_neighbors = []  # one list shared by all graphs
        color_changes_within_iteration = [None]*len(sorted_vertices_list)

        former_index_list = [0]*len(sorted_vertices_list)
        current_index_list = [0]*len(sorted_vertices_list)
        converged = [True]*len(sorted_vertices_list)
        done = False
        while not done:
            done = True  # if all graphs have checked all their colors this boolean will remain true
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
                        # check whether neighbors equal to an already defined neighbor-color pair
                        found = False
                        index = MergeAndSearchTools.search_vertex_color_and_neighbors(
                            color_and_neighbors, curr_neighbors, 0)
                        if index != -1:
                            # neighbors equal to neighbors of already seen vertex:
                            # change color to color of this vertex if necessary (could already be that color)
                            if sorted_vertices_list[i][j].get_colornum() != color_and_neighbors[index][0]:
                                if color_changes_within_iteration[i] is None:
                                    color_changes_within_iteration[i] = []
                                color_changes_within_iteration[i].append(
                                    (sorted_vertices_list[i][j].get_label(), color_and_neighbors[index][0]))
                                graph_info_list[i].swap_colors(
                                    color_and_neighbors[index][0], sorted_vertices_list[i][j].get_colornum())
                                converged[i] = False
                            found = True
                        if not found:
                            # unique neighbor combination found among all graphs: hand out new color
                            max_color += 1
                            graph_info_list[i].swap_colors(max_color, sorted_vertices_list[i][j].get_colornum())
                            if color_changes_within_iteration[i] is None:
                                color_changes_within_iteration[i] = []
                            color_changes_within_iteration[i].append(
                                (sorted_vertices_list[i][j].get_label(), max_color))
                            color_and_neighbors = MergeAndSearchTools.zip_vertex_color_and_neighbors(
                                color_and_neighbors, (max_color, curr_neighbors))
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
                # done with current color in all graphs: update isomorphism table,
                # finalize color changes and clear start color, changes and neighbor lists
                for entry in isomorphic[:]:
                    if graph_info_list[entry[0]].get_num_of_a_color(start_color) != \
                            graph_info_list[entry[1]].get_num_of_a_color(start_color):
                        isomorphic.remove(entry)
                for i in range(0, len(sorted_vertices_list)):
                    if color_changes_within_iteration[i] is not None:
                        sorted_to_label_changes = MergeAndSearchTools.sort_vertex_label(
                            sorted_vertices_list[i][former_index_list[i]:current_index_list[i]])
                        # noinspection PyTypeChecker
                        for entry in color_changes_within_iteration[i]:
                            sorted_to_label_changes[MergeAndSearchTools.search_vertex_label(
                                sorted_to_label_changes, entry[0])].set_colornum(entry[1])
                start_color = None
                color_changes_within_iteration = [None]*len(sorted_vertices_list)
                color_and_neighbors = []

        for i in range(0, len(sorted_vertices_list)):
            graph_info_list[i].set_has_converged(not graph_info_list[i].has_duplicate_colors() or converged[i])
        return max_color

def testIsoSpeed(num_of_graphs, num_of_vertices):
    gi_finder = GIFinder(num_of_graphs, num_of_vertices, False, True)
    t = time()
    x,y,z,a = gi_finder.find_isomorphisms()
    print('>> Run time:', time() - t, 'sec.')

# Test run of the 49 and 4098 vertex graphs
#testIsoSpeed(2, 49)
testIsoSpeed(6, 15)
#testIsoSpeed(4, 9)
#testIsoSpeed(4, 16)
#testIsoSpeed(6, 15)