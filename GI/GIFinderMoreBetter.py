import MergeAndSearchTools
from graphIO import writeDOT, loadgraph
import basicgraphs
from GraphInfo import GraphInfo
from time import time
from basicgraphs import graph
import basicpermutationgroup
import copy, math

"""
Class for finding graph iso- / automorphisms
"""


class GIFinder():

    def __init__(self, location, pre_process, save_results=False, print_non_final_info=False):
        self._save_results = save_results
        self._print_non_final_info = print_non_final_info
        self._location = None
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
        try:
            self._graph_list_original = loadgraph('Graphs/' + location + '.grl', readlist=True)[0]
        except FileNotFoundError:
            self._graph_list_original = loadgraph('Graphs/' + location + '.gr', readlist=True)[0]
        self._location = location

    def get_graph(self):
        return loadgraph('Graphs/' + self._location + '.grl', readlist=True)[0]

    def find_twins(self):
        #graph_list = self._graph_list_original
        graph_list = graph(5)
        graph_list.addedge(graph_list[0],graph_list[1])
        graph_list.addedge(graph_list[0],graph_list[2])
        graph_list.addedge(graph_list[0],graph_list[3])
        graph_list.addedge(graph_list[1],graph_list[3])
        graph_list.addedge(graph_list[1],graph_list[2])
        graph_list = [graph_list]
        sorted_vertices_list, graph_info_list = self.color_all_vertices_by_degree(graph_list)
        #copy_sorted_vertices_list, copy_graph_info_list = self.color_all_vertices_by_degree([graph_list])

        # part I - initial coloring (also sorts to color)
        # sorted_vertices_list, graph_info_list = self.color_all_vertices_by_degree(graph_list)

        if graph_info_list[0].has_duplicate_colors():
            print(self.find_false_twins_rec(graph_list, sorted_vertices_list, graph_info_list))
            print(self.find_true_twins_rec(graph_list, sorted_vertices_list, graph_info_list))

    def try_non_trivial_orbit_rec(self, stab, cntr):
        nontrivorb = basicpermutationgroup.FindNonTrivialOrbit(stab)
        if nontrivorb != None:
            orb = basicpermutationgroup.Orbit(stab, nontrivorb)
            stab = basicpermutationgroup.Stabilizer(stab, nontrivorb)
            print(stab, orb)
            return len(orb) * self.try_non_trivial_orbit_rec(stab, cntr+1)
        else:
            return 1

    def find_automorphisms(self, search_for_isos=True):

        # part I - initial coloring (also sorts to color)
        graph_list = copy.deepcopy(self._graph_list_original)

        sorted_vertices_list, graph_info_list = self.color_all_vertices_by_degree(graph_list)
        if (search_for_isos):

            new_isos = self.find_isomorphisms()

            print('Sets of isomorphic graphs: Number of automorphisms:')
            for i in range(0, len(new_isos)):
                sorted_graph_lists = [sorted_vertices_list[new_isos[i][0]], copy.deepcopy(sorted_vertices_list[new_isos[i][0]])]
                graph_info_lists = [graph_info_list[new_isos[i][0]], graph_info_list[new_isos[i][0]].get_copy()]
                graph_info_lists[1].set_graph_id(1)
                isomorphic = [(0, 1)]

                # part II - recursive coloring
                self.color_vertices_by_neighbor_rec(None, sorted_graph_lists, graph_info_lists, isomorphic)

                # part III - find automorphisms
                counter = self.graphs_count_automorphisms_slow(None, sorted_graph_lists, graph_info_lists, isomorphic[0])
                print(new_isos[i],' ',counter)
        else:
            print('Sets of isomorphic graphs -Number of automorphisms')
            for i in range(0, len(sorted_vertices_list)):
                sorted_graph_lists = [sorted_vertices_list[i], copy.deepcopy(sorted_vertices_list[i])]
                graph_info_lists = [graph_info_list[i], graph_info_list[i].get_copy()]
                graph_info_lists[1].set_graph_id(1)
                isomorphic = [(0, 1)]

                # part II - recursive coloring
                self.color_vertices_by_neighbor_rec(None, sorted_graph_lists, graph_info_lists, isomorphic)

                # part III - find automorphisms
                counter = self.graphs_count_automorphisms_slow(None, sorted_graph_lists, graph_info_lists, isomorphic[0])
                print([i],' ',counter)
        return 0

    def find_isomorphisms(self):

        graph_list = self._graph_list_original

        if len(graph_list) == 1:
            graph_list.append(self.get_graph()[0])

        # part I - initial coloring (also sorts to color)
        sorted_vertices_list, graph_info_list = self.color_all_vertices_by_degree(graph_list)
        # sorted_vertices_list = [None] * len(graph_list)
        # graph_info_list = [None] * len(graph_list)
        # for i in range(0, len(graph_list)):
        #     sorted_vertices_list[i] = MergeAndSearchTools.sort_vertex_color(graph_list[i].V())
        #     graph_info_list[i] = GraphInfo(i)

        automorphisms = [1]*len(graph_list)
        if self._pre_process:
            # part I.2 pre-processing: twins
            if graph_info_list[0].has_duplicate_colors():
                automorphisms = self.find_false_twins_rec(graph_list, sorted_vertices_list, graph_info_list)
                automorphisms2 = self.find_true_twins_rec(graph_list, sorted_vertices_list, graph_info_list)
                for i in range(0, len(automorphisms)):
                    automorphisms[i] *= automorphisms2[i]

        # vertex_copy =

        isomorphic = []
        # adds all graphs with the same number of colors to the list of possibly isomorphic graphs
        for i in range(0, len(graph_info_list)):
            for j in range(i + 1, len(graph_info_list)):
                if graph_info_list[i].num_of_colors() == graph_info_list[j].num_of_colors():
                    isomorphic.append((i, j))


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

        numbers_seen = []
        for i in range(0, len(new_isos)):
            for j in range(0, len(new_isos[i])):
                numbers_seen.append(new_isos[i][j])
        numbers_seen = MergeAndSearchTools.sort_number(numbers_seen)

        for i in range(0, len(graph_list)):
            if MergeAndSearchTools.search_number(numbers_seen, i, 0) == -1:
                new_isos.append([i])
        return new_isos

    def find_false_twins_rec(self, graph_list, sorted_vertices_list, graph_info_list):
        print('Finding false twins...')
        stable = False
        all_automorphisms = [1]*len(sorted_vertices_list)
        non_iso_graphs = []
        # it might be that it is always stable after one (two) iterations
        counter = 0
        while not stable:
            stable = True
            # get twins of every graph
            all_twins = []
            twins_to_be_removed = []
            for index, entry in enumerate(sorted_vertices_list):
                twins, remove, automorphisms = self.find_false_twins(entry, graph_info_list[index])
                print(index, automorphisms, twins)
                all_twins.append(twins)
                all_automorphisms[index] *= automorphisms
                twins_to_be_removed.append(remove)
                if len(twins) > 0:
                    stable = False
            if stable:
                break
            # get max color
            max_color = graph_info_list[0].max_number()
            for i in range(1, len(graph_info_list)):
                if graph_info_list[i].max_number() > max_color:
                    max_color = graph_info_list[i].max_number()
            # remove twins from graphs
            print('max_color:', max_color)
            print('twins:', all_twins)
            print('remove:', twins_to_be_removed)
            print(sorted_vertices_list)
            self.remove_twins_from_graph_and_color(graph_list, sorted_vertices_list, graph_info_list, all_twins, twins_to_be_removed, max_color)
            print(sorted_vertices_list)
            counter += 1
        print(counter)
        return all_automorphisms

    # a twin cannot be a twin on its own
    def find_false_twins(self, sorted_vertices_list_item, graph_info_list_item):
        # first sort vertices_list_item to the labels of the neighbors of the nodes <- difficult!
        sorted_vertices_list_item = MergeAndSearchTools.sort_vertex_color_and_nbs_to_label(sorted_vertices_list_item)
        automorphisms = 1
        twins_to_be_removed = []
        twins = []
        curr_color_twins = []
        curr_color_nbs_twins = [sorted_vertices_list_item[0]]
        curr_color = sorted_vertices_list_item[0].colornum()
        curr_nbs = sorted_vertices_list_item[0].nbs_sorted_to_label()
        for i in range(1, len(sorted_vertices_list_item)):
            if curr_color == sorted_vertices_list_item[i].colornum():
                if MergeAndSearchTools.compare_vertex_label_equal(curr_nbs, sorted_vertices_list_item[i].nbs_sorted_to_label()):
                    curr_color_nbs_twins.append(sorted_vertices_list_item[i])
                else:
                    if len(curr_color_nbs_twins) > 1:
                        curr_color_twins.append(curr_color_nbs_twins)
                        # first will not be removed, but we the only one left
                        twins_to_be_removed.extend(curr_color_nbs_twins[1:])
                        # update automorphisms
                        automorphisms *= self.factorial(len(curr_color_nbs_twins))
                    curr_color_nbs_twins = [sorted_vertices_list_item[i]]
                    curr_nbs = sorted_vertices_list_item[i].nbs_sorted_to_label()
            else:
                # if we were inside nbs list save this
                if len(curr_color_nbs_twins) > 1:
                    curr_color_twins.append(curr_color_nbs_twins)
                    twins_to_be_removed.extend(curr_color_nbs_twins[1:])
                    automorphisms *= self.factorial(len(curr_color_nbs_twins))
                curr_color_nbs_twins = [sorted_vertices_list_item[i]]
                curr_nbs = sorted_vertices_list_item[i].nbs_sorted_to_label()
                # if we were inside color list save this
                if len(curr_color_twins) > 0:
                    twins.append(curr_color_twins)
                curr_color_twins = []
                curr_color = sorted_vertices_list_item[i].colornum()
        # if we were inside nbs list save this
        if len(curr_color_nbs_twins) > 1:
            curr_color_twins.append(curr_color_nbs_twins)
            twins_to_be_removed.extend(curr_color_nbs_twins[1:])
            automorphisms *= self.factorial(len(curr_color_nbs_twins))
        # if we were inside color list save this
        if len(curr_color_twins) > 0:
            twins.append(curr_color_twins)
        return twins, MergeAndSearchTools.sort_vertex_label_rem_dups(twins_to_be_removed), automorphisms

    def find_true_twins_rec(self, graph_list, sorted_vertices_list, graph_info_list):
        stable = False
        all_automorphisms = [1]*len(sorted_vertices_list)
        non_iso_graphs = []
        # it might be that it is always stable after one (two) iterations
        while not stable:
            stable = True
            # get twins of every graph
            all_twins = []
            twins_to_be_removed = []
            for index, entry in enumerate(sorted_vertices_list):
                twins, remove, automorphisms = self.find_true_twins(entry, graph_info_list[index])
                print(index, automorphisms, twins)
                all_twins.append(twins)
                all_automorphisms[index] *= automorphisms
                twins_to_be_removed.append(remove)
                if len(twins) > 0:
                    stable = False
            if stable:
                break
            # compare twin lists if more than one graph
            if len(all_twins) > 1:
                for i in range(0, len(all_twins)):
                    for j in range(i + 1, len(all_twins)):
                        # naïve, but fast: compare only automorphisms
                        if len(all_twins[i]) != len(all_twins[j]):
                            non_iso_graphs.append((i, j))
            # get max color
            max_color = graph_info_list[0].max_number()
            for i in range(1, len(graph_info_list)):
                if graph_info_list[i].max_number() > max_color:
                    max_color = graph_info_list[i].max_number()
            # remove twins from graphs
            self.remove_twins_from_graph_and_color(graph_list, sorted_vertices_list, graph_info_list, all_twins, twins_to_be_removed, max_color)
        return all_automorphisms

    # a twin cannot be a twin on its own
    def find_true_twins(self, sorted_vertices_list_item, graph_info_list_item):
        # first sort vertices_list_item to the labels of the neighbors of the nodes <- difficult!
        sorted_vertices_list_item = MergeAndSearchTools.sort_vertex_color_and_nbs_to_label(sorted_vertices_list_item)
        automorphisms = 1
        twins_to_be_removed = []
        twins = []
        curr_color_twins = []
        curr_color_nbs_twins = [sorted_vertices_list_item[0]]
        curr_color = sorted_vertices_list_item[0].colornum()

        curr_nbs = sorted_vertices_list_item[0].nbs_sorted_to_label()
        index0 = MergeAndSearchTools.zip_nodes_label(curr_nbs, sorted_vertices_list_item[0])

        for i in range(1, len(sorted_vertices_list_item)):
            if curr_color == sorted_vertices_list_item[i].colornum():
                comp_nodes = sorted_vertices_list_item[i].nbs_sorted_to_label()
                index1 = MergeAndSearchTools.zip_nodes_label(comp_nodes, sorted_vertices_list_item[i])
                if MergeAndSearchTools.compare_vertex_label_equal(curr_nbs, comp_nodes):
                    curr_color_nbs_twins.append(sorted_vertices_list_item[i])
                else:
                    if len(curr_color_nbs_twins) > 1:
                        curr_color_twins.append(curr_color_nbs_twins)
                        # first will not be removed, but we the only one left
                        twins_to_be_removed.extend(curr_color_nbs_twins[1:])
                        # update automorphisms
                        automorphisms *= self.factorial(len(curr_color_nbs_twins))
                    curr_color_nbs_twins = [sorted_vertices_list_item[i]]
                    curr_nbs = sorted_vertices_list_item[i].nbs_sorted_to_label()

            else:
                # if we were inside nbs list save this
                if len(curr_color_nbs_twins) > 1:
                    curr_color_twins.append(curr_color_nbs_twins)
                    twins_to_be_removed.extend(curr_color_nbs_twins[1:])
                    automorphisms *= self.factorial(len(curr_color_nbs_twins))
                curr_color_nbs_twins = [sorted_vertices_list_item[i]]
                curr_nbs = sorted_vertices_list_item[i].nbs_sorted_to_label()
                index1 = MergeAndSearchTools.zip_nodes_label(curr_nbs, sorted_vertices_list_item[i])
                # if we were inside color list save this
                if len(curr_color_twins) > 0:
                    twins.append(curr_color_twins)
                curr_color_twins = []
                curr_color = sorted_vertices_list_item[i].colornum()
        # if we were inside nbs list save this
        if len(curr_color_nbs_twins) > 1:
            curr_color_twins.append(curr_color_nbs_twins)
            twins_to_be_removed.extend(curr_color_nbs_twins[1:])
            automorphisms *= self.factorial(len(curr_color_nbs_twins))
        # if we were inside color list save this
        if len(curr_color_twins) > 0:
            twins.append(curr_color_twins)
        return twins, MergeAndSearchTools.sort_vertex_label_rem_dups(twins_to_be_removed), automorphisms

    def factorial(self, value):
        if value == 0:
            return 1
        elif value <= 2:
            return value
        else:
            fact = 2
            for i in range(3, value + 1):
                fact *= i
            return fact

    def findFalseTwins(self, sorted_vertices_list, graph_info_list):
        nbs_tuple = []
        twins = []
        if graph_info_list[0].has_duplicate_colors():
            double_colors = MergeAndSearchTools.sort_pairs(graph_info_list[0].get_duplicate_colors(), 0)
            index = 0
            for i in range (0, len(sorted_vertices_list[0])):
                if sorted_vertices_list[0][i].get_colornum() == double_colors[index][0]:
                    for j in range (0, double_colors[index][1]):
                        nbs_tuple.append((sorted_vertices_list[0][i],MergeAndSearchTools.sort_vertex_label(sorted_vertices_list[0][i].nbs())))
                        i=i+1
                    if (index == len(double_colors)-1):
                        break
                    else:
                        index+=1
            old = 0
            for i in range(0, len(nbs_tuple)):
                if (i < len(nbs_tuple)-1):
                    if (nbs_tuple[i][0].get_colornum() == nbs_tuple[i+1][0].get_colornum()):
                        if (i-old > 0):
                            nbs_tuple[old:i] = MergeAndSearchTools.sort_tuple_list(nbs_tuple[old:i])
                            old = i+1
                else:
                    if (i-old > 0):
                        nbs_tuple[old:i] = MergeAndSearchTools.sort_tuple_list(nbs_tuple[old:i])
            for i in range(0, len(nbs_tuple)):
                if (i < len(nbs_tuple)-1):
                    if (nbs_tuple[i][0].get_colornum() == nbs_tuple[i+1][0].get_colornum()):
                        if (MergeAndSearchTools.compare_vertex_label(nbs_tuple[i][1],nbs_tuple[i+1][1])) == 0:
                            twins.append([nbs_tuple[i][0].get_label(),nbs_tuple[i+1][0].get_label()])
                        else:
                            continue
        return MergeAndSearchTools.zip_tuples_isomorphisms(twins)

    def remove_twins_from_graph_and_color(self, graphs, vertices, graph_info_list, twins_of_all_graphs, twins_to_be_removed, max_color):
        print('Changing twin colors...')
        color_matches = [] # [curr_color [num_of_twins, new_color]] sorted to first two items
        for i in range(0, len(twins_of_all_graphs)):
            for j in range(0, len(twins_of_all_graphs[i])):
                # sort twins of one color to amount of nodes within one twin
                twins_of_all_graphs[i][j] = MergeAndSearchTools.sort_pairs_to_len(twins_of_all_graphs[i][j]) # TODO is this necessary?
                current_color = twins_of_all_graphs[i][j][0][0].colornum()
                index_of_color = MergeAndSearchTools.search_pairs(color_matches, current_color, 0, 0)
                if index_of_color == -1:
                    # color not encountered yet: add it with empty coloring list
                    item = [current_color]
                    item.append([])
                    color_matches, index_of_color = MergeAndSearchTools.zip_tuple(color_matches, item, 0)
                for k in range(0, len(twins_of_all_graphs[i][j])):
                    curr_num_of_twins = len(twins_of_all_graphs[i][j][k])
                    index_num_of_twins = MergeAndSearchTools.search_pairs(color_matches[index_of_color][1], curr_num_of_twins, 0, 0)
                    if index_num_of_twins == -1:
                        # twins with this current color and this number of elements have not been encountered yet: add it and color accordingly
                        max_color += 1
                        new_item = (curr_num_of_twins, max_color)
                        color_matches[index_of_color][1], index_num_of_twins = MergeAndSearchTools.zip_tuple(color_matches[index_of_color][1], new_item, 0)
                        graph_info_list[i].swap_colors(max_color, twins_of_all_graphs[i][j][k][0].colornum())
                        print('swap new', i, twins_of_all_graphs[i][j][k][0].get_label(), 'len=' + str(len(twins_of_all_graphs[i][j][k])), ':', twins_of_all_graphs[i][j][k][0].colornum(), '->', max_color, ':', graph_info_list[i].get_all_colors())
                        twins_of_all_graphs[i][j][k][0].set_colornum(max_color)
                    else:
                        color = color_matches[index_of_color][1][index_num_of_twins][1]
                        graph_info_list[i].swap_colors(color, twins_of_all_graphs[i][j][k][0].colornum())
                        print('swap curr', i, twins_of_all_graphs[i][j][k][0].get_label(), 'len=' + str(len(twins_of_all_graphs[i][j][k])), ':', twins_of_all_graphs[i][j][k][0].colornum(), '->', color, ':', graph_info_list[i].get_all_colors())
                        twins_of_all_graphs[i][j][k][0].set_colornum(color)
        print('colormatches:', color_matches)
        # finally remove twins from all graphs
        for i in range(0, len(twins_to_be_removed)):
            graphs[i].update_edges(twins_to_be_removed[i], graph_info_list[i])
            vertices[i] = MergeAndSearchTools.sort_vertex_color(graphs[i].V())

        return vertices

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

    def graphs_count_automorphisms_fast(self, graph_list, sorted_vertices_list, graph_info_list, tuple, automorphism_list_full, depth, parent_trivial_vertex):
        if not graph_info_list[tuple[1]].has_duplicate_colors():
            automorphism_list = []
            for i in range(0, len(sorted_vertices_list[tuple[1]])):
                automorphism_list.append((sorted_vertices_list[tuple[1]][i].get_label()))
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
                #for p in range(0, depth):
                #    print(end=' ')
                #print(depth, i, max_color, tuple)

                # copy the vertices, info lists and indices to try coloring
                color_copy_1 = MergeAndSearchTools.copy_colors(sorted_vertices_list[tuple[1]])
                graph_info_list_copy = MergeAndSearchTools.copy_graph_info(graph_info_list)
                indices_copy = []
                for entry in indices[1]:
                    indices_copy.append(entry)

                # change the color of one dub in the other graph and re-sort (wisely)
                graph_info_list_copy[tuple[1]].swap_colors(max_color, double_colors[a][0])
                sorted_vertices_list[tuple[1]] = self.recolor_and_sort(sorted_vertices_list[tuple[1]], indices_copy, i, max_color)

                if i==0 and a==0 and parent_trivial_vertex:
                    trivial_vertex = True
                else:
                    trivial_vertex = False

                # copy vertex list (just the list, no deep-copying)
                tuple_list = [tuple]
                sorted_vertices_list_copy = []
                for entry in sorted_vertices_list:
                    sorted_vertices_list_copy.append(entry)

                # main step : recursively color neighbors of graphs until coloring is stable again
                self.color_vertices_by_neighbor_rec(graph_list, sorted_vertices_list_copy, graph_info_list_copy, tuple_list)

                if len(tuple_list) > 0:
                    return_to_trivial_vertex, automorphism_list_full = \
                        self.graphs_count_automorphisms_fast(graph_list, sorted_vertices_list_copy, graph_info_list_copy, tuple, automorphism_list_full, depth+ 1, trivial_vertex)
                    if return_to_trivial_vertex and not trivial_vertex:
                        return True, automorphism_list_full

                sorted_vertices_list[tuple[0]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[tuple[0]], color_copy_0)
                sorted_vertices_list[tuple[1]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[tuple[1]], color_copy_1)

        return False, automorphism_list_full

    def graphs_count_automorphisms_slow(self, graph_list, sorted_vertices_list, graph_info_list, tuple):
        if not graph_info_list[tuple[0]].has_duplicate_colors():
            return 1

        counter=0
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
        graph_info_list[tuple[0]].set_has_converged(False)
        graph_info_list[tuple[1]].set_has_converged(False)

        # change the color of one dub in the first graph and re-sort (wisely)
        graph_info_list[tuple[0]].swap_colors(max_color, double_colors[0][0])
        sorted_vertices_list[tuple[0]] = self.recolor_and_sort(sorted_vertices_list[tuple[0]], indices[0], 0, max_color)
        self.check_integrity(sorted_vertices_list[tuple[0]], graph_info_list[tuple[0]])

        color_copy_0 = MergeAndSearchTools.copy_colors(sorted_vertices_list[tuple[0]])

        for i in range(0, len(indices[1])):

            # some nice status printing
            #for p in range(0, depth):
            #    print(end=' ')
            #print(depth, 'i=' + str(i), 'mcol=' + str(max_color), end=' ')

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
            self.color_vertices_by_neighbor_rec(graph_list, sorted_vertices_list_copy, gi_list, tuple_list)

            if len(tuple_list) > 0:
                counter += self.graphs_count_automorphisms_slow(graph_list, sorted_vertices_list_copy, gi_list, tuple)

            sorted_vertices_list[tuple[1]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[tuple[1]], color_copy_1)
            sorted_vertices_list[tuple[0]] = MergeAndSearchTools.restore_colors(sorted_vertices_list[tuple[0]], color_copy_0)

        return counter

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
        graph_info_list[tuple[0]].set_has_converged(False)
        if tuple[0] != tuple[1]:
            graph_info_list[tuple[1]].set_has_converged(False)

        # change the color of one dub in the first graph and re-sort (wisely)
        graph_info_list[tuple[0]].swap_colors(max_color, double_colors[0][0])
        sorted_vertices_list[tuple[0]] = self.recolor_and_sort(sorted_vertices_list[tuple[0]], indices[0], 0, max_color)
        # self.check_integrity(sorted_vertices_list[tuple[0]], graph_info_list[tuple[0]])

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
            # self.check_integrity(sorted_vertices_list[tuple[1]], graph_info_list_copy_1)

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
                # if converged:
                sorted_vertices_list[i] = MergeAndSearchTools.sort_vertex_color(sorted_vertices_list[i])
                # else:
                    # sorted_vertices_list[i] = MergeAndSearchTools.sort_vertex_color(sorted_vertices_list[i])
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
        # changes = [None]*len(graph_info_list) TODO

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
                # done_with_graph = False TODO
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
                # if done_with_graph:
                    # current_index_list[i] = len(sorted_vertices_list[i])
                if broke:
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
                                sorted_to_label_changes, entry[0], 0)]
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
    # t = time()
    # gi_finder = GIFinder('basicGI1', True, False, True)
    # x = gi_finder.find_isomorphisms() # find_isomorphisms()
    # print('>> Run time', time() - t, 'sec.')

    t = time()
    gi_finder = GIFinder('Cographs1', True, False, True)
    x = gi_finder.find_isomorphisms() # find_isomorphisms()
    print('>> Run time', time() - t, 'sec.')

    # t = time()
    # gi_finder = GIFinder('bonusGI2', True, False, True)
    # x = gi_finder.find_isomorphisms() # find_isomorphisms()
    # print('>> Run time', time() - t, 'sec.')
    #
    # t = time()
    # gi_finder = GIFinder('bonusGI3', False, False, True)
    # x = gi_finder.find_isomorphisms() # find_isomorphisms()
    # print('>> Run time', time() - t, 'sec.')
    #
    # t = time()
    # gi_finder = GIFinder('bonusGI4', True, False, True)
    # x = gi_finder.find_isomorphisms() # find_isomorphisms()
    # print('>> Run time', time() - t, 'sec.')

test_iso_speed()
