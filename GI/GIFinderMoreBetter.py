import MergeAndSearchTools
from graphIO import writeDOT, loadgraph
import basicgraphs
from GraphInfo import GraphInfo
from time import time
import threading
import basicpermutationgroup
import copy

"""
Class for finding graph iso- / automorphisms
"""


class GIFinder():

    def __init__(self, location, pre_process, save_results=False, print_non_final_info=False):
        self._save_results = save_results
        self._print_non_final_info = print_non_final_info
        self.read_graph(location)
        self._pre_process = pre_process

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

        for i in range(0, len(sorted_vertices_list)):
            sorted_graph_lists = [sorted_vertices_list[i], copy.deepcopy(sorted_vertices_list[i])]
            graph_info_lists = [graph_info_list[i], graph_info_list[i].get_copy()]
            graph_info_lists[1].set_graph_id(1)
            isomorphic = [(0, 1)]

            # part II - recursive coloring
            self.color_vertices_by_neighbor_rec(None, sorted_graph_lists, graph_info_lists, isomorphic)

            # part III - find automorphisms
            done, permutations = self.graphs_count_automorphisms(None, sorted_graph_lists, graph_info_lists, isomorphic[0], list(), 0)
            non_triv_orb = basicpermutationgroup.FindNonTrivialOrbit(permutations)
            orb = basicpermutationgroup.Orbit(permutations, non_triv_orb)
            stab = basicpermutationgroup.Stabilizer(permutations, non_triv_orb)
            print('Orbit(' + str(non_triv_orb) + '):', orb)
            print('Stab(' + str(non_triv_orb) + '):', stab)
            print('Order:', len(orb) * len(stab))

        return 0

    def find_isomorphisms(self):

        graph_list = self.graph_list_original

        # part I - initial coloring (also sorts to color)
        sorted_vertices_list, graph_info_list = self.color_all_vertices_by_degree(graph_list)

        isomorphic = []
        # adds all graphs with the same number of colors to the list of possibly isomorphic graphs
        if len(graph_info_list) == 1:
            isomorphic.append((0, 0))
        for i in range(0, len(graph_info_list)):
            for j in range(i + 1, len(graph_info_list)):
                if graph_info_list[i].num_of_colors() == graph_info_list[j].num_of_colors():
                    isomorphic.append((i, j))

        if self._pre_process:
            # part I.2 pre-processing: twins
            graph_list[0].find_false_twins()

        # part II - recursive coloring
        print('- Recursive coloring...')
        print('Iterations:', self.color_vertices_by_neighbor_rec(graph_list, sorted_vertices_list, graph_info_list, isomorphic))

        # update colors of nodes in graph (only done when saving results)
        if self._save_results:
            for i in range(0, len(graph_info_list)):
                sorted_to_label_vertices = MergeAndSearchTools.sort_vertex_label(sorted_vertices_list[i])
                for j in range(0, len(sorted_to_label_vertices)):
                    graph_list[i].V()[j].set_colornum(
                        sorted_to_label_vertices[graph_list[i].V()[j].get_label()].get_colornum())

        # for sorted_vertex_list in sorted_vertices_list: TODO
        #     for entry in sorted_vertex_list:
        #         entry.set_nbs_color_changed(False)

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
        print('Sets of isomorphic graphs:')
        if len(new_isos) > 0:
            for entry in new_isos:
                print(entry)
        else:
            print('None')
        return new_isos

    def match_pairs_rec(self, graph_list, sorted_vertices_list, graph_info_list, todo, matches):
        temp_matches = []
        temp_mismatches = []

        # copy colors of first graph (always the same one so is only done once)
        color_copy_0 = MergeAndSearchTools.copy_colors(sorted_vertices_list[todo[0][0]])

        for entry in todo:
            # copy colors of second graph
            color_copy_1 = MergeAndSearchTools.copy_colors(sorted_vertices_list[entry[1]])

            # find isomorphism's
            is_isomorphic = self.graphs_have_isomorphisms(self, graph_list, sorted_vertices_list,
                                                          MergeAndSearchTools.copy_graph_info(graph_info_list), entry, 0)
            # reset colors of both graphs
            sorted_vertices_list[entry[0]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[entry[0]], color_copy_0)
            sorted_vertices_list[entry[1]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[entry[1]], color_copy_1)

            if is_isomorphic:
                print('Iso-pair:', entry)
                temp_matches.append(entry)
            else:
                print('Non-iso-pair:', entry)
                temp_mismatches.append(entry[1])
        matches.extend(temp_matches)
        if len(temp_mismatches) >= 2:
            todo = MergeAndSearchTools.blow_tuples_isomorphisms_list(temp_mismatches)
        else:
            return matches
        return self.match_pairs_rec(graph_list, sorted_vertices_list, graph_info_list, todo, matches)

    def graphs_count_automorphisms(self, graph_list, sorted_vertices_list, graph_info_list, tuple, automorphism_list_full, depth, parent_trivial_vertex=True):
        if not graph_info_list[tuple[0]].has_duplicate_colors():
            automorphism_list = []
            for i in range(0, len(sorted_vertices_list[0])):
                automorphism_list.append(sorted_vertices_list[1][i].get_label())
            if len(automorphism_list) > 0 and automorphism_list not in automorphism_list_full:
                automorphism_list_full.append(basicpermutationgroup.permutation(len(automorphism_list), mapping=automorphism_list))
            return True, automorphism_list_full

        # get all (color, # of dubs) which occur more than once per graph, sorted to amount of dubs
        double_colors = graph_info_list[tuple[0]].get_duplicate_colors()

        for a in range(0, len(double_colors)):
            # find those colors within the vertex lists
            indices = [[(0, MergeAndSearchTools.search_vertex_color(sorted_vertices_list[tuple[0]], double_colors[0][0], 0))]]
            indices.append(MergeAndSearchTools.search_vertex_color_dup(sorted_vertices_list[tuple[1]], double_colors[a][0]))
            for index, entry in enumerate(indices[1]):
                indices[1][index] = (index, entry)

            # get the maximum used color number
            max_color = graph_info_list[tuple[0]].max_number()
            if graph_info_list[tuple[1]].max_number() > max_color:
                max_color = graph_info_list[tuple[1]].max_number()
            max_color += 1

            # change the color of one dub in the first graph and re-sort (wisely)
            graph_info_list[tuple[0]].swap_colors(max_color, double_colors[0][0])
            sorted_vertices_list[tuple[0]] = self.recolor_and_sort(sorted_vertices_list[tuple[0]], indices[0], 0, max_color)

            color_copy_0 = MergeAndSearchTools.copy_colors(sorted_vertices_list[tuple[0]])

            # this boolean could be true (and should be reset) from former color refinement tasks
            graph_info_list[tuple[0]].set_has_converged(False)
            graph_info_list[tuple[1]].set_has_converged(False)
            for i in range(0, len(indices[1])):
                if i == 0 and parent_trivial_vertex:
                    trivial_vertex = True
                else:
                    trivial_vertex = False

                for p in range(0, depth):
                    print(end=' ')
                print(depth, i, max_color, tuple)

                # copy the vertices, info lists and indices to try coloring
                color_copy_1 = MergeAndSearchTools.copy_colors(sorted_vertices_list[tuple[1]])
                graph_info_list_copy = MergeAndSearchTools.copy_graph_info(graph_info_list)
                indices_copy = []
                for entry in indices[1]:
                    indices_copy.append(entry)

                # change the color of one dub in the other graph and re-sort (wisely)
                graph_info_list_copy[tuple[1]].swap_colors(max_color, double_colors[a][0])
                sorted_vertices_list[tuple[1]] = self.recolor_and_sort(sorted_vertices_list[tuple[1]], indices_copy, i, max_color)

                # copy vertex list (just the list, no deep-copying)
                tuple_list = [tuple]
                sorted_vertices_list_copy = []
                for entry in sorted_vertices_list:
                    sorted_vertices_list_copy.append(entry)

                # main step : recursively color neighbors of graphs until coloring is stable again
                self.color_vertices_by_neighbor_rec(graph_list, sorted_vertices_list_copy, graph_info_list_copy, tuple_list)

                if len(tuple_list) > 0:
                    return_to_trivial_vertex, automorphism_list_full = \
                        self.graphs_count_automorphisms(graph_list, sorted_vertices_list_copy, graph_info_list_copy, tuple, automorphism_list_full, depth + 1)

                    if return_to_trivial_vertex and not trivial_vertex:
                        return return_to_trivial_vertex, automorphism_list_full

                sorted_vertices_list[tuple[0]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[tuple[0]], color_copy_0)
                sorted_vertices_list[tuple[1]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[tuple[1]], color_copy_1)
        return False, automorphism_list_full

    @staticmethod
    def graphs_have_isomorphisms(self, graph_list, sorted_vertices_list, graph_info_list, tuple, depth):
        if not graph_info_list[tuple[0]].has_duplicate_colors():
            return 1

        # get all (color, # of dubs) which occur more than once per graph, sorted to amount of dubs
        double_colors = graph_info_list[tuple[0]].get_duplicate_colors()

        # find those colors within the vertex lists
        indices = [[(0, MergeAndSearchTools.search_vertex_color(sorted_vertices_list[tuple[0]], double_colors[0][0], 0))]]
        indices.append(MergeAndSearchTools.search_vertex_color_dup(sorted_vertices_list[tuple[1]], double_colors[0][0]))
        for index, entry in enumerate(indices[1]):
            indices[1][index] = (index, entry)

        # get the maximum used color number
        max_color = graph_info_list[tuple[0]].max_number()
        if graph_info_list[tuple[1]].max_number() > max_color:
            max_color = graph_info_list[tuple[1]].max_number()
        max_color += 1

        # this boolean could be true (and should be reset) from former color refinement tasks
        # graph_info_list[tuple[0]].set_has_converged(False) TODO
        # graph_info_list[tuple[1]].set_has_converged(False)

        # change the color of one dub in the first graph and re-sort (wisely)
        graph_info_list[tuple[0]].swap_colors(max_color, double_colors[0][0])
        sorted_vertices_list[tuple[0]] = self.recolor_and_sort(sorted_vertices_list[tuple[0]], indices[0], 0, max_color)

        color_copy_0 = MergeAndSearchTools.copy_colors(sorted_vertices_list[tuple[0]])

        for i in range(0, len(indices[1])):

            # some nice status printing
            for p in range(0, depth):
                print(end=' ')
            print(depth, 'i=' + str(i), 'mcol=' + str(max_color), end=' ')

            # copy the vertices, info lists and indices to try coloring (and be able to undo this)
            graph_info_list_copy_0 = graph_info_list[tuple[0]].get_copy()
            color_copy_1 = MergeAndSearchTools.copy_colors(sorted_vertices_list[tuple[1]])
            graph_info_list_copy_1 = graph_info_list[tuple[1]].get_copy()
            indices_copy = []
            for entry in indices[1]:
                indices_copy.append(entry)

            # change the color of one dub in the other graph and re-sort (wisely)
            graph_info_list_copy_1.swap_colors(max_color, double_colors[0][0])
            sorted_vertices_list[tuple[1]] = self.recolor_and_sort(sorted_vertices_list[tuple[1]], indices_copy, i, max_color)

            # # set all neighbors to be changed an re-sort after <- might be inefficient TODO make this work :)
            # sorted_vertices_list[tuple[0]][indices[0][0][1]].set_nbs_color_changed(True)
            # for entry in sorted_vertices_list[tuple[0]][indices[0][0][1]].nbs():
            #     entry.set_nbs_color_changed(True)
            # sorted_vertices_list[tuple[1]][indices_copy[i][1]].set_nbs_color_changed(True)
            # for entry in sorted_vertices_list[tuple[1]][indices_copy[i][1]].nbs():
            #     entry.set_nbs_color_changed(True)

            # sorted_vertices_list[tuple[0]] = MergeAndSearchTools.sort_vertex_color_and_changed(sorted_vertices_list[tuple[0]])
            # sorted_vertices_list[tuple[1]] = MergeAndSearchTools.sort_vertex_color_and_changed(sorted_vertices_list[tuple[1]])

            # copy vertex list (just the list, no deep-copying)
            tuple_list = [tuple]
            sorted_vertices_list_copy = []
            for entry in sorted_vertices_list:
                sorted_vertices_list_copy.append(entry)

            # copy graph info list (just the list, no deep-copying)
            gi_list = [None]*len(graph_info_list)
            gi_list[tuple[0]] = graph_info_list_copy_0
            gi_list[tuple[1]] = graph_info_list_copy_1

            # main step : recursively color neighbors of graphs until coloring is stable again
            print('it=' + str(self.color_vertices_by_neighbor_rec(graph_list, sorted_vertices_list_copy, gi_list, tuple_list)), tuple)

            if len(tuple_list) > 0:
                iso_found = self.graphs_have_isomorphisms(self, graph_list, sorted_vertices_list_copy, gi_list, tuple, depth + 1)
                if iso_found:
                    return True
            # reset colors of both graphs
            sorted_vertices_list[tuple[0]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[tuple[0]], color_copy_0)
            sorted_vertices_list[tuple[1]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[tuple[1]], color_copy_1)

        return False

    # Checks graph info with graph
    # WARNING: very slow!
    def check_integrity(self, sorted_vertices_list_item, graph_info_list_item):
        # check amount of each color
        num_of_unique_colors = 0
        curr_color = -1
        amount_of_a_color = 0
        for item in sorted_vertices_list_item:
            if item.colornum() == curr_color:
                amount_of_a_color += 1
            else:
                # check amount of a color
                if curr_color != -1 and amount_of_a_color != graph_info_list_item.get_num_of_a_color(curr_color):
                    print('Fail-color-amount:', curr_color, ":", amount_of_a_color, '!=', graph_info_list_item.get_num_of_a_color(curr_color))
                    print('Vertices:', sorted_vertices_list_item)
                    print('GraphInfo:', graph_info_list_item.get_all_colors())
                    pass
                elif curr_color != -1 and amount_of_a_color > 1 and not graph_info_list_item.has_duplicate_colors():
                    print('Fail-color-dups:', curr_color)
                    print('Vertices:', sorted_vertices_list_item)
                    print('GraphInfo:', graph_info_list_item.get_all_colors())
                    pass
                curr_color = item.colornum()
                amount_of_a_color = 1
                num_of_unique_colors += 1
        # check total amount of colors
        if num_of_unique_colors != graph_info_list_item.num_of_colors():
            print('Fail-total:', num_of_unique_colors, '!=', graph_info_list_item.num_of_colors())
            print('Vertices:', sorted_vertices_list_item)
            print('GraphInfo:', graph_info_list_item.get_all_colors())
            pass

    def color_all_vertices_by_degree(self, graph_list):
        print('- Initial coloring...')
        graph_info_list = [None]*len(graph_list)
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
            graph.V()[j].set_colornumm(curr_deg, False)
            graph_info.bulk_increment_colors(curr_deg)
        graph_info.bulk_final_sort()
        if self._save_results:
            writeDOT(graph, ('Results/colorful_' + str(graph.get_label()) + '.dot'))
        return graph_info

    def color_vertices_by_neighbor_rec(self, graph_list, sorted_vertices_list, graph_info_list, isomorphic):
        """
        Recursively colors of the vertices according to their neighbors for all graphs in parallel.
        :return:
        """
        if len(isomorphic) == 0:
            return
        max_color = -1
        for i in range(0, len(graph_info_list)):
            if graph_info_list[i] is not None and graph_info_list[i].max_number() > max_color:
                max_color = graph_info_list[i].max_number()
        iteration_counter = 0
        converged = False
        while not converged:
            for i in range(0, len(sorted_vertices_list[:])):
                if MergeAndSearchTools.search_pairs(isomorphic, i, 0, 0) == -1 \
                        and MergeAndSearchTools.search_pairs(
                            MergeAndSearchTools.sort_pairs(isomorphic, 1), i, 1, 0) == -1:
                    sorted_vertices_list[i] = []
            # print('Iteration', iteration_counter)
            max_color = self.color_vertices_by_neighbors(sorted_vertices_list, graph_info_list, max_color, isomorphic)
            converged = True
            if len(isomorphic) == 0:
                converged = True
            elif len(isomorphic) == 1:
                if not graph_info_list[isomorphic[0][0]].has_converged() \
                        or not graph_info_list[isomorphic[0][1]].has_converged():
                    converged = False
            else:
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
                # sort the vertices
                if converged:
                    sorted_vertices_list[i] = MergeAndSearchTools.sort_vertex_color(sorted_vertices_list[i])
                else:
                    sorted_vertices_list[i] = MergeAndSearchTools.sort_vertex_color(sorted_vertices_list[i])
                    # sorted_vertices_list[i] = MergeAndSearchTools.sort_vertex_color_and_changed(sorted_vertices_list[i]) TODO
            iteration_counter += 1
        return iteration_counter

    # Colors the vertices by the color of their neighbors according to three rules:
    #   - if two vertices already have different colors this will remain the same
    #   - if two vertices have the same color but differently colored neighbors, one of them will change color
    #   - if two vertices had the same color, but have now changed color
    #     this color will be the same iff both have equally colored neighbors
    # Should be called iteratively until the coloring is stable (has diverged)
    @staticmethod
    def color_vertices_by_neighbors(sorted_vertices_list, graph_info_list, max_color, isomorphic):
        changes = [None]*len(graph_info_list)

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
                done_with_graph = False
                broke = False
                if current_index_list[i] >= len(sorted_vertices_list[i]):
                    continue
                for j in range(current_index_list[i], len(sorted_vertices_list[i])):
                    done = False
                    # if not sorted_vertices_list[i][j].is_nbs_color_changed(): TODO
                    #     done_with_graph = True
                    #     break
                    if start_color is None:
                        # sorted_vertices_list[i][j].set_nbs_color_changed(False) TODO
                        start_color = sorted_vertices_list[i][j].get_colornum()
                        color_and_neighbors = [(start_color, sorted_vertices_list[i][j].nbs())]
                        continue
                    elif sorted_vertices_list[i][j].get_colornum() == start_color:
                        # sorted_vertices_list[i][j].set_nbs_color_changed(False) TODO
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
                    else:
                        broke = True
                        break
                # done with current color in this graph: update former and current index
                former_index_list[i] = current_index_list[i]
                if done_with_graph:
                    current_index_list[i] = len(sorted_vertices_list[i])
                elif broke:
                    current_index_list[i] = j
                else:
                    current_index_list[i] = j + 1
            if not done:
                # done with current color in all graphs: update isomorphism table,
                # finalize color changes and clear start color, changes and neighbor lists
                if start_color is not None:
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
                            changed_one = sorted_to_label_changes[MergeAndSearchTools.search_vertex_label(
                                sorted_to_label_changes, entry[0])]
                            changed_one.set_colornum(entry[1])
                            # if changes[i] is None: TODO
                            #     changes[i] = []
                            # changes[i].append(changed_one)
                            # changes[i].extend(changed_one.nbs())
                start_color = None
                color_changes_within_iteration = [None]*len(sorted_vertices_list)
                color_and_neighbors = []

        for i in range(0, len(sorted_vertices_list)):
            if graph_info_list[i] is not None:
                graph_info_list[i].set_has_converged(not graph_info_list[i].has_duplicate_colors() or converged[i])

        # # calculate changes for (possible) next iteration
        # for change in changes:
        #     if change is not None:
        #         change = MergeAndSearchTools.sort_vertex_label_rem_dups(change)
        #         for entry in change:
        #             entry.set_nbs_color_changed(True) TODO
        return max_color

    def recolor_and_sort(self, vertices_list, indices, vertex_index, new_color):
        if len(indices) > 1 and indices[0] > indices[1]:
            pass
        vertex = vertices_list.pop(indices[vertex_index][1])
        vertex.set_colornum(new_color)
        vertices_list = MergeAndSearchTools.zip_nodes(vertices_list, vertex)
        nummertje = indices[vertex_index][1]
        indices = MergeAndSearchTools.sort_pairs(indices, 1)
        index = MergeAndSearchTools.search_pairs(indices, nummertje, 1, 0)
        for i in range(index + 1, len(indices)):
            indices[i] = (indices[i][0], indices[i][1] - 1)
        indices = MergeAndSearchTools.sort_pairs(indices, 0)
        indices[vertex_index] = (indices[vertex_index][0], len(vertices_list) - 1)
        return vertices_list

def test_iso_speed():
    t = time()
    gi_finder = GIFinder('modulesD', False, False, True)
    x = gi_finder.find_isomorphisms()
    print('>> Run time', time() - t, 'sec.')

test_iso_speed()
