import pdb

from graphIO import writeDOT, loadgraph
from graphinfo import GraphInfo

"""
Class for finding graph isomorphisms

DEPRECATED - Use GIFinderMoreBetter instead!
Only contains old coloring method for reference
"""

class GIFinder():

    def __init__(self, num_graphs=4, num_vertices=4098, save_results=False, print_non_final_info=False):
        self._num_graphs = num_graphs
        self._num_vertices = num_vertices
        self._save_results = save_results
        self._print_non_final_info = print_non_final_info

    def __repr__(self):
        return str(self._graph_id)

    def find_isomorphisms_old(self):
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
    def color_vertices_by_neighbors_old(self, sortedVertices, graph_info):
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

gifinder = GIFinder(6, 15, True, True)
gifinder.solve_non_isomorphic()