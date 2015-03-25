import MergeAndSearchTools
from graphIO import writeDOT, loadgraph
from GraphInfo import GraphInfo
from time import time
import copy

"""
Class for finding graph isomorphisms
"""


class GIFinder():

    def __init__(self, location, save_results=False, print_non_final_info=False):
        self._save_results = save_results
        self._print_non_final_info = print_non_final_info
        self.read_graph(location)
        self.graph_list_original


    def __repr__(self):
        return str(self._num_graphs) + '-' + str(self._num_vertices)

    def read_graph(self, location):
        print('Finding Graph Isomorphisms in graph file:', location)

        # initialisation part of the algorithm which loads the graphs from a file
        print('- Loading graphs...')
        # graph_list = loadgraph('Graphs/crefBM_'
        #                    + str(self._num_graphs) + '_' + str(self._num_vertices) + '.grl', readlist=True)[0]
        #'Graphs/bigtrees1.grl'
        self.graph_list_original = loadgraph('Graphs/' + location + '.grl', readlist=True)[0]

    def find_automorphisms(self):

        graph_list = self.graph_list_original

        # part I - initial coloring (also sorts to color)
        sorted_vertices_list, graph_info_list = self.color_all_vertices_by_degree(graph_list)
        for i in range(0,len(graph_list)):
            graph_lists = [sorted_vertices_list[i], copy.deepcopy(sorted_vertices_list[i])]
            graph_info_lists = [graph_info_list[i], copy.deepcopy(graph_info_list[i])]
            graph_info_lists[1].set_graph_id(1)
            isomorphic = [(0,1)]

            # part II - recursive coloring
            self.color_vertices_by_neighbor_rec(None, graph_lists, graph_info_lists, isomorphic)

            # part III - find automorphisms
            nr_of_isos = self.graphs_have_isomorphisms(None, graph_lists, graph_info_lists, isomorphic[0], True)
            print('isos ',i,' ',nr_of_isos)

        return nr_of_isos

    def find_isomorphisms(self):

        graph_list = self.graph_list_original

        # part I - initial coloring (also sorts to color)
        sorted_vertices_list, graph_info_list = self.color_all_vertices_by_degree(graph_list)

        isomorphic = []
        # adds all graphs with the same number of colors to the list of possibly isomorphic graphs
        for i in range(0, len(graph_info_list)):
            for j in range(i + 1, len(graph_info_list)):
                if graph_info_list[i].num_of_colors() == graph_info_list[j].num_of_colors():
                    isomorphic.append((i, j))

        # part II - recursive coloring
        print('- Recursive coloring...')
        self.color_vertices_by_neighbor_rec(graph_list, sorted_vertices_list, graph_info_list, isomorphic)

        # update colors of nodes in graph (only done when saving results)
        if self._save_results:
            for i in range(0, len(graph_info_list)):
                sorted_to_label_vertices = MergeAndSearchTools.sort_vertex_label(sorted_vertices_list[i])
                for j in range(0, len(sorted_to_label_vertices)):
                    graph_list[i].V()[j].set_colornum(
                        sorted_to_label_vertices[graph_list[i].V()[j].get_label()].get_colornum())

        # recursively get rid of duplicates or remove iso if proven impossible
        isomorphic_zipped = MergeAndSearchTools.zip_tuples_isomorphisms(isomorphic[:])
        new_isos = []
        undecided_found = False
        for entry in isomorphic_zipped[:]:
            if graph_info_list[entry[0]].has_duplicate_colors():
                print('Undecided found -', entry)
                undecided_found = True
                isos = MergeAndSearchTools.zip_tuples_isomorphisms(
                    self.match_pairs_rec(graph_list, sorted_vertices_list, graph_info_list,
                                         MergeAndSearchTools.blow_tuples_isomorphisms_list(entry), []))
                if len(isos) > 0:
                    new_isos.extend(isos)
            else:
                new_isos.append(entry)
        if not undecided_found:
            print('No undecided found')

        # Part IV all isomorphisms found, print and return results
        print('- Matching graphs...')
        if len(new_isos) > 0:
            for i in range(0, len(new_isos)):
                print('Isomorphism found between: ', end='')
                first = True
                for j in range(0, len(new_isos[i])):
                    if first:
                        print(new_isos[i][j], end='')
                        first = False
                    elif j < len(new_isos[i]) - 1:
                        print(',', new_isos[i][j], end='')
                    else:
                        print(' and', new_isos[i][j])
        else:
            print('No Isomorphisms found between the graphs')
        return new_isos


    def match_pairs_rec(self, graph_list, sorted_vertices_list, graph_info_list, todo, matches):
        at_least_one_match = False
        temp_matches = []
        temp_mismatches = []
        for entry in todo:
            # copy current colors
            color_copy_0 = MergeAndSearchTools.copy_colors(sorted_vertices_list[entry[0]])
            color_copy_1 = MergeAndSearchTools.copy_colors(sorted_vertices_list[entry[1]])

            # find isomorphism's
            is_isomorphic = self.graphs_have_isomorphisms(graph_list, sorted_vertices_list,
                                                          MergeAndSearchTools.copy_graph_info(graph_info_list), entry, False)
            # reset colors of both graphs
            sorted_vertices_list[entry[0]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[entry[0]], color_copy_0)
            sorted_vertices_list[entry[1]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[entry[1]], color_copy_1)

            if is_isomorphic:
                print('Iso-pair:', entry)
                temp_matches.append(entry)
                at_least_one_match = True
            else:
                print('Non-iso-pair:', entry)
                temp_mismatches.append(entry[1])
        matches.extend(temp_matches)
        if len(temp_mismatches) >= 2:
            todo = MergeAndSearchTools.blow_tuples_isomorphisms_list(temp_mismatches)
        else:
            return matches
        return self.match_pairs_rec(graph_list, sorted_vertices_list, graph_info_list, todo, matches)

    def graphs_have_isomorphisms(self, graph_list, sorted_vertices_list, graph_info_list, tuple, find_all=False):
        if not graph_info_list[tuple[0]].has_duplicate_colors():
            return 1

        iso_count = 0

        # get all (color, # of dubs) which occur more than once per graph, sorted to amount of dubs
        double_colors = graph_info_list[tuple[0]].get_duplicate_colors()

        if find_all==False:
            amount_loops=1
        else:
            amount_loops=len(double_colors)

        for a in range(0, amount_loops):
            # find those colors within the vertex lists
            indices = [[MergeAndSearchTools.search_vertex_color(sorted_vertices_list[tuple[0]], double_colors[a][0], 0)]]
            indices.append(MergeAndSearchTools.search_vertex_color_dup(sorted_vertices_list[tuple[1]], double_colors[a][0]))

            # change the color of one dub in the first graph and re-sort
            max_color = graph_info_list[tuple[0]].max_number()
            if graph_info_list[tuple[1]].max_number() > max_color:
                max_color = graph_info_list[tuple[1]].max_number()
                print('success')
            max_color += 1

            graph_info_list[tuple[0]].set_changed(True)
            graph_info_list[tuple[0]].swap_colors(max_color, double_colors[0][0])
            sorted_vertices_list[tuple[0]] = self.recolor_and_sort(sorted_vertices_list[tuple[0]], indices[0], 0, max_color)

            for i in range(0, len(indices[1])):
                # copy the vertices, info lists and indices to try coloring
                #sorted_vertices_list_copy = copy.deepcopy(sorted_vertices_list)
                color_copy_0 = MergeAndSearchTools.copy_colors(sorted_vertices_list[tuple[0]])
                color_copy_1 = MergeAndSearchTools.copy_colors(sorted_vertices_list[tuple[1]])
                graph_info_list_copy = MergeAndSearchTools.copy_graph_info(graph_info_list)
                indices_copy = []
                for entry in indices[1]:
                    indices_copy.append(entry)

                # change the color of one dub in the other graph and re-sort
                graph_info_list_copy[tuple[1]].set_changed(True)
                graph_info_list_copy[tuple[1]].swap_colors(max_color, double_colors[a][0])
                sorted_vertices_list[tuple[1]][indices_copy[i]].set_colornum(max_color)
                sorted_vertices_list[tuple[1]] = self.recolor_and_sort(sorted_vertices_list[tuple[1]], indices_copy, i, max_color)

                # recursively color neighbors of graphs until coloring is stable again
                tuple_list = [tuple]
                sorted_vertices_list_copy = []
                for entry in sorted_vertices_list:
                    sorted_vertices_list_copy.append(entry)

                # max_color
                # main step : re-color graphs
                self.color_vertices_by_neighbor_rec(graph_list, sorted_vertices_list_copy, graph_info_list_copy, tuple_list)

                if len(tuple_list) > 0:
                    iso_count += self.graphs_have_isomorphisms(graph_list, sorted_vertices_list_copy, graph_info_list_copy, tuple, find_all)
                    if not find_all:
                        if iso_count >= 1:
                            return 1
                    else:
                        sorted_vertices_list[tuple[0]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[tuple[0]], color_copy_0)
                        sorted_vertices_list[tuple[1]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[tuple[1]], color_copy_1)
                # reset colors of both graphs
                else:
                    sorted_vertices_list[tuple[0]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[tuple[0]], color_copy_0)
                    sorted_vertices_list[tuple[1]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[tuple[1]], color_copy_1)
        return iso_count

    def color_all_vertices_by_degree(self, graph_list):
        print('- Initial coloring...')
        graph_info_list = [None]*len(graph_list)
        sorted_vertices_list = [None]*len(graph_list)
        for i, entry in enumerate(graph_list):
            print('Graph', i, 'of', len(graph_list) - 1)
            entry.set_label(i)
            graph_info_list[i] = self.color_vertices_by_degree(entry)
            # sort list of vertices of graph to color
            sorted_vertices_list[i] = MergeAndSearchTools.sort_vertex_color(entry.V())
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
            graph_info.bulk_increment_colors(curr_deg)
        graph_info.bulk_final_sort()
        #if self._save_results:
            #writeDOT(graph, ('Results/colorful_' + str(graph.get_label()) + '.dot'))
        return graph_info

    def color_vertices_by_neighbor_rec(self, graph_list, sorted_vertices_list, graph_info_list, isomorphic):
        """
        Recursively colors of the vertices according to their neighbors for all graphs in parallel.
        :return:
        """
        #print('- Recursive coloring...')
        max_color = graph_info_list[0].max_number()
        for i in range(1, len(graph_info_list)):
            if graph_info_list[i].max_number() > max_color:
                max_color = graph_info_list[i].max_number()
                print('success 2')
        iteration_counter = 0
        converged = False
        #print('---', max_color)
        while not converged:
            for i in range(0, len(sorted_vertices_list[:])):
                if MergeAndSearchTools.search_pairs(isomorphic, i, 0, 0) == -1 \
                        and MergeAndSearchTools.search_pairs(
                            MergeAndSearchTools.sort_pairs(isomorphic, 1), i, 1, 0) == -1:
                    sorted_vertices_list[i] = []
            #print('Iteration', iteration_counter)
            max_old = max_color
            max_color = self.color_vertices_by_neighbors(sorted_vertices_list, graph_info_list, max_color, isomorphic)
            #print('-', format((100*(graph_info_list[0].num_of_colors() / self._num_vertices)), '.2f'), '%')
            converged = True
            for i in range(0, len(sorted_vertices_list)):
                if not graph_info_list[i].has_converged():
                    converged = False
                    break
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
                    if i == 1 and j == 20:
                        pass
                    done = False
                    if start_color is None:
                        start_color = sorted_vertices_list[i][j].get_colornum()
                        color_and_neighbors = [(start_color, sorted_vertices_list[i][j].nbs())]
                        continue
                    elif sorted_vertices_list[i][j].get_colornum() == start_color:
                        curr_neighbors = sorted_vertices_list[i][j].nbs()
                        # check whether neighbors equal to an already defined neighbor-color pair
                        found = False
                        try:
                            index = MergeAndSearchTools.search_vertex_color_and_neighbors(
                                    color_and_neighbors, curr_neighbors, 0)
                        except IndexError:
                            print('faal 1:', max_color, ', (', i, ',', j, ')', color_and_neighbors, '(', sorted_vertices_list[i][j].get_colornum(), curr_neighbors, ') ',sorted_vertices_list[i])
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
                            #print(max_color - 1, '->', max_color, ', (', i, ',', j, ')',  color_and_neighbors, '!= (', sorted_vertices_list[i][j].get_colornum(), curr_neighbors, ')')
                            graph_info_list[i].swap_colors(max_color, sorted_vertices_list[i][j].get_colornum())
                            if color_changes_within_iteration[i] is None:
                                color_changes_within_iteration[i] = []
                            color_changes_within_iteration[i].append(
                                (sorted_vertices_list[i][j].get_label(), max_color))
                            try:
                                color_and_neighbors = MergeAndSearchTools.zip_vertex_color_and_neighbors(
                                    color_and_neighbors, (max_color, curr_neighbors))
                            except IndexError:
                                print('faal 2:', max_color, ', (', i, j, ')',  color_and_neighbors, '(', sorted_vertices_list[i][j].get_colornum(), curr_neighbors, ')')
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


    def recolor_and_sort(self, vertices_list, indices, vertex_index, new_color):
        vertex = vertices_list.pop(indices[vertex_index])
        vertex.set_colornum(new_color)
        vertices_list = MergeAndSearchTools.zip_nodes(vertices_list, vertex)
        indices[vertex_index] = len(vertices_list) - 1
        for i in range(vertex_index + 1, len(indices)):
            indices[i] -= 1
        return vertices_list

def testIsoSpeed():
    gi_finder = GIFinder('cographs1', False, True)
    t = time()
    x = gi_finder.find_automorphisms()
    print(x)
    print('>> Run time:', time() - t, 'sec.')


testIsoSpeed()
