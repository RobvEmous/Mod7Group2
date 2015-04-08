import MergeAndSearchTools

"""
This is a module for working with *undirected* graphs (simple graphs or multigraphs).

It contains three classes: vertex, edge and graph. 

The interface of these classes is extensive and allows programming all kinds of graph algorithms.

NOT THE CASE ANYMORE - However, the data structure used is quite basic and inefficient: a graph object stores only a vertex list and an edge list, and methods such as adjacency testing / finding neighbors of a vertex require going through the entire edge list!
--> Listing vertices, edges, direct neighbors and adjacency testing is now implemented with roughly O(log n) complexity. Note that only simple graphs are currently supported
"""
# version: 29-01-2015, Paul Bonsma & Rob van Emous & Joshua de Bie

unsafe=True
# Set to True for faster, but unsafe listing of all vertices and edges.

class GraphError(Exception):
    def __init__(self,message):
        self.mess=message

    def __str__(self):
        return self.mess


class vertex():
    """
    Vertex objects have an attribute <_graph> pointing to the graph they are part of,
    and an attribute <_label> which can be anything: it is not used for any methods,
    except for __repr__.
    """
    def __init__(self, graph, label=0):
        """
        Creates a vertex, part of <graph>, with optional label <label>.
        (Labels of different vertices may be chosen the same; this does
        not influence correctness of the methods, but will make the string
        representation of the graph ambiguous.)
        """
        self._graph=graph
        self._label=label
        self._colornum = 0
        self._nbs_updated = True
        self._nbs_sorted = False
        self._nbs_sorted_to_label = False
        self._nbs_color_changed = True
        self._nbs_list = []
        self._nbs_list_label = []

    def __repr__(self):
        return str(self._label)

    def get_label(self):
        return self._label

    def get_graph(self):
        return self._graph

    def colornum(self):
        return self._colornum

    def get_colornum(self):
        return self._colornum

    def set_colornumm(self, num, update_nbs):
        self._colornum = num
        if update_nbs:
            for nb in self.nbs():
                nb.set_nbs_sorted(False)
                nb.set_nbs_sorted_to_label(False)

    def set_colornum(self, num):
        self.set_colornumm(num, True)

    def is_nbs_color_changed(self):
        return self._nbs_color_changed

    def set_nbs_color_changed(self, is_changed):
        self._nbs_color_changed = is_changed

    def set_nbs_updated(self, is_updated):
        self._nbs_updated = is_updated

    def set_nbs_sorted(self, is_sorted):
        self._nbs_sorted = is_sorted

    def set_nbs_sorted_to_label(self, is_sorted):
        self._nbs_sorted_to_label = is_sorted

    def nbss(self, sort_nbs_list):
        """
        Returns the list of neighbors of vertex <self>.
        In case of parallel edges: duplicates are not removed from this list!
        It will only (re)calculate the neighbors if necessary for better performance
        """
        if self._nbs_updated or len(self._nbs_list) == 0:
            for e in self.inclist():
                self._nbs_list.append(e.otherend(self))
            self._nbs_updated = False
        if sort_nbs_list and not self._nbs_sorted:
            self._nbs_list = MergeAndSearchTools.sort_vertex_color(self._nbs_list)
            self._nbs_sorted = True
        return self._nbs_list

    def nbs(self):
        return self.nbss(True)

    def nbs_sorted_to_label(self):
        if self._nbs_updated or len(self._nbs_list_label) == 0:
            # this might be sorted to color
            self._nbs_list_label = self.nbss(False)
            self._nbs_sorted_to_label = False
        if not self._nbs_sorted_to_label:
            self._nbs_list_label = MergeAndSearchTools.sort_vertex_label(self._nbs_list_label)
            self._nbs_sorted_to_label = True
        return self._nbs_list_label

    def deg(self):
        """
        Returns the degree of vertex <self>.
        """
        return len(self.nbss(False))

    def adj(self,other):
        """
        Returns True iff vertex <self> is adjacent to <other> vertex.
        """
        return self._graph.adj(self,other)

    def inclist(self):
        """
        Returns the list of edges incident with vertex <self>.

        old algorithm:

        incl=[]
        for e in self._graph._E:
            if e.incident(self):
                incl.append(e)
        """
        incl=[]
        Start_index = self._graph.findFirstEdgeOfVertex(self._label)
        index = Start_index
        while True:
            edge = self._graph._EDouble[index]
            if edge._tail._label == self._label:
                incl.append(edge)
                if index < len(self._graph._EDouble) - 1:
                    index += 1
                else:
                    break
            else:
                break
        if Start_index == 0:
            return incl
        index = Start_index - 1
        while True:
            edge = self._graph._EDouble[index]
            if edge._tail._label == self._label:
                incl.append(edge)
                if index > 0:
                    index -= 1
                else:
                    break
            else:
                break
        return incl

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

class edge():
    """
    Edges have attributes <_tail> and <_head> which point to the end vertices
    (vertex objects). The order of these is arbitrary (undirected edges).
    """
    def __init__(self,tail,head):
        """
        Creates an edge between vertices <tail> and <head>.
        """
        # tail and head must be vertex objects.
        if not tail._graph==head._graph:
            raise GraphError(
                'Can only add edges between vertices of the same graph')
        self._tail=tail
        self._head=head

    def __repr__(self):
        return '('+str(self._tail)+','+str(self._head)+')'

    def tail(self):
        return self._tail

    def head(self):
        return self._head

    def otherend(self,oneend):
        """
        Given one end vertex <oneend> of the edge <self>, this returns
        the other end vertex of <self>.
        """
        # <oneend> must be either the head or the tail of this edge.
        if self._tail==oneend:
            return self._head
        elif self._head==oneend:
            return self._tail
        raise GraphError(
            'edge.otherend(oneend): oneend must be head or tail of edge')

    def incident(self,vertex):
        """
        Returns True iff the edge <self> is incident with the
        vertex <vertex>.
        """
        if self._tail==vertex or self._head==vertex:
            return True
        else:
            return False

class graph():
    """
    A graph object has as main attributes:
     <_V>: the list of its vertices
     <_E>: the list of its edges, these are sorted when used for searching (for O(log n) instead of O(n) performance)
    In addition:
     <_simple> is True iff the graph must stay simple (used when trying to add edges)
     <_directed> is False for now (feel free to write a directed variant of this
         module)
     <_nextlabel> is used to assign default labels to vertices.
    """
    unsorted = False

    def __init__(self, n=0, simple=False):
        """
        Creates a graph.
        Optional argument <n>: number of vertices.
        Optional argument <simple>: indicates whether the graph should stay simple.
        """
        self._V = []
        self._E = []
        self._EDouble = []
        self._directed = False
        # may be changed later for a more general version that can also
        # handle directed graphs.
        self._simple = simple
        self._nextlabel = 0
        for i in range(n):
            self.addvertex()
        self._label = 0

    def __repr__(self):
        return 'V='+str(self._V)+'\nE='+str(self._E)

    def __getitem__(self,i):
        """
        Returns the <i>th vertex of the graph -- as given in the vertex list;
        this is not related to the vertex labels.
        """
        return self._V[i]

    def get_label(self):
        return self._label

    def set_label(self, label):
        self._label = label

    def V(self):
        """
        Returns the list of vertices of the graph.
        """
        if unsafe:	# but fast
            return self._V
        else:
            return self._V[:]	# return a *copy* of this list

    def set_V(self, V):
        self._V = V

    def E(self):
        """
        Returns the list of edges of the graph.
        """
        if unsafe:	# but fast
            return self._E
        else:
            return self._E[:]	# return a *copy* of this list

    def EDouble(self):
        """
        Returns the list of edges of the graph.
        """
        if unsafe:	# but fast
            return self._EDouble
        else:
            return self._EDouble[:]	# return a *copy* of this list

    def set_changed(self, changed):
        if changed:
            for i in range(0, len(self._V)):
                self._V[i].set_changed(True)

    def addvertex(self,label=-1):
        """
        Add a vertex to the graph.
        Optional argument: a vertex label (arbitrary)
        """
        if label==-1:
            label=self._nextlabel
            self._nextlabel+=1
        u=vertex(self,label)
        self._V.append(u)
        self._changed = True
        return u

    def addedge(self,tail,head):
        """
        Add an edge to the graph between <tail> and <head>.
        Includes some checks in case the graph should stay simple.
        """
        if tail._label > head._label:
            tail, head = head, tail
        if self._simple:
            if tail==head:
                raise GraphError('No loops allowed in simple graphs')
            for e in self._E:
                if (e._tail==tail and e._head==head):
                    raise GraphError(
                        'No multiedges allowed in simple graphs')
                if not self._directed:
                    if (e._tail==head and e._head==tail):
                        raise GraphError(
                            'No multiedges allowed in simple graphs')
        if not (tail._graph==self and head._graph==self):
            raise GraphError(
                'Edges of a graph G must be between vertices of G')
        e1=edge(tail,head)
        self._E.append(e1)
        self._EDouble.append(e1)
        e2=edge(head,tail)
        self._EDouble.append(e2)
        self.unsorted = True
        self._changed = True
        return e1

    def sortEdgesRec(self, edges, index):
        if len(edges) > 1:
            i = int((len(edges) / 2))
            f = self.sortEdgesRec(edges[:i], index)
            s = self.sortEdgesRec(edges[i:], index)
            r = []
            fi = si = 0
            while fi < len(f) and si < len(s):
                if index == 0:
                    if f[fi].tail().get_label() < s[si].tail().get_label() \
                            or f[fi].tail().get_label() == s[si].tail().get_label() and f[fi].head().get_label() <= s[si].head().get_label():
                        r.append(f[fi])
                        fi += 1
                    else:
                        r.append(s[si])
                        si += 1
                else:
                    if f[fi].head().get_label() < s[si].head().get_label() \
                            or f[fi].head().get_label() == s[si].head().get_label() and f[fi].tail().get_label() <= s[si].tail().get_label():
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
            return edges

    def sortEdges(self):
        self._EDouble = self.sortEdgesRec(self._EDouble, 0)
        self.unsorted = False

    def expand_edges(self): # TODO verify
        self._EDouble = [None] * len(self._E)
        self._EDouble.extend(self._E)
        for index, entry in enumerate(self._E):
            self._EDouble[index] = edge(entry.head(), entry.tail())
        self._EDouble = self.sortEdgesRec(self._EDouble, 0)
        self.unsorted = False

    def update_edges(self, to_be_removed, graph_info_list_item):
        # sort to first element
        self._E = self.sortEdgesRec(self._E, 0)

        for entry in to_be_removed:
            # remove vertex
            graph_info_list_item.decrement_num_of_a_color(entry.colornum()) # should not be forgotten
            print('rem curr', self.get_label(), entry.get_label(), ':', entry.colornum(), '->', 'None', ':', graph_info_list_item.get_all_colors())
            self._V.remove(entry)


            # search an edge left-wise
            index = self.binary_search_pairs(self._E, entry.get_label())
            if index != -1:
                first_index = index
                # search first
                while first_index > 0:
                    if self._E[first_index - 1].tail().get_label() == entry.get_label():
                        first_index -= 1
                    else:
                        break
                # search last
                last_index = index
                while last_index < len(self._E):
                    if self._E[last_index].tail().get_label() == entry.get_label():
                        last_index += 1
                    else:
                        break
                # remove edges
                del self._E[first_index:last_index]

        # re-sort to second element
        self._E = self.sortEdgesRec(self._E, 1)

        for entry in to_be_removed:

            # search an edge right-wise
            index = self.binary_search_pairs_reverse(self._E, entry.get_label())
            if index != -1:
                first_index = index
                # search first
                while first_index > 0:
                    if self._E[first_index - 1].head().get_label() == entry.get_label():
                        first_index -= 1
                    else:
                        break
                # search last
                last_index = index
                while last_index < len(self._E):
                    if self._E[last_index].head().get_label() == entry.get_label() :
                        last_index += 1
                    else:
                        break
                # remove edges
                del self._E[first_index:last_index]

        # finally expand _E to _EDouble
        self.expand_edges()


    # uses binary algorithm to search for (first) elements in lists containing edge tupels
    def binary_search_pairs(self, list, value):
        if len(list) > 0:
            l = 0
            h = len(list) - 1
            while h - l > 0 and list[l].tail().get_label() != value:
                m = int((l + h) / 2)
                if list[m].tail().get_label() == value:
                    l = m
                elif list[m].tail().get_label() < value:
                    l = m + 1
                else:
                    h = m - 1
            if list[l].tail().get_label() == value:
                return l
            else:
                return -1
        else:
            return -1

    # uses binary algorithm to search for (first) elements in lists containing edge tupels
    def binary_search_pairs_reverse(self, list, value):
        if len(list) > 0:
            l = 0
            h = len(list) - 1
            while h - l > 0 and list[l].head().get_label() != value:
                m = int((l + h) / 2)
                if list[m].head().get_label() == value:
                    l = m
                elif list[m].head().get_label() < value:
                    l = m + 1
                else:
                    h = m - 1
            if list[l].head().get_label() == value:
                return l
            else:
                return -1
        else:
            return -1

    def findFirstEdgeOfVertex(self, label):
        if self.unsorted:
            self.sortEdges()
        return self.binary_search_pairs(self._EDouble, label)


    def find_edge_rec(self, u, v, max, min):
        """
        If <u> and <v> are adjacent, this returns an edge between them.
        (Arbitrary in the case of multigraphs.)
        Otherwise this returns <None>.

        for e in self._EDouble:
            if (e._tail==u and e._head==v) or (e._tail==v and e._head==u):
                return e
        return None
        """
        print(max)
        print(min)
        if max == min:
            return None
        if u < v:
            high = v
            low = u
        else:
            high = u
            low = v
        e = self._EDouble
        b = max - min
        i = (b // 2) + min
        if e[i][1] == high and e[i][0]==low:
            return e[i]
        elif i == len(e) - 1:
            return None
        elif e[i][0] < low or e[i][1] < high:
            return self.find_edge_rec(u, v, max, i)
        elif e[i][0] > low or e[i][1] > high:
            return self.find_edge_rec(u, v, i, min)
        return None

    def find_edge(self,u,v):
        if self.unsorted == True:
            self.sortEdges()
        return self.find_edge_rec(u, v, len(self._EDouble), 0)

    def adj(self,u,v):
        """
        Returns True iff vertices <u> and <v> are adjacent.
        """
        if self.find_edge(u,v) == None:
            return False
        else:
            return True

    def is_directed(self):
        """
        Returns False, because for now these graphs are always undirected.
        """
        return self._directed


def get_copy(vertex_list):
    # create copy of graph
    new_graph = graph()

    vertex_list[0].get_graph()
    # new_graph.
    new_vertex_list = []
    for entry in vertex_list:
        new_vertex = vertex(entry.get_graph(), entry.get_label())
        new_vertex.set_V(entry.V())
        new_vertex.set_changed(True)
        new_vertex_list.append(new_vertex)
    return new_vertex_list