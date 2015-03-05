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
    def __init__(self,graph,label=0):
        """
        Creates a vertex, part of <graph>, with optional label <label>.
        (Labels of different vertices may be chosen the same; this does
        not influence correctness of the methods, but will make the string
        representation of the graph ambiguous.)
        """
        self._graph=graph
        self._label=label
        self._colornum = 0
        self._changed = True
        self._sorted = False
        self._nbs_list = []

    def __repr__(self):
        return str(self._label)

    def get_label(self):
        return self._label

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

    def colornum(self):
        return self._colornum

    def get_colornum(self):
        return self._colornum

    def set_colornum(self, num):
        self._colornum = num
        for nb in self.nbs():
            nb.set_sorted = False

    def set_changed(self, changed):
        self._changed = changed

    def set_sorted(self, sorted):
        self._sorted = sorted

    def nbs(self):
        """
        Returns the list of neighbors of vertex <self>.
        In case of parallel edges: duplicates are not removed from this list!
        """
        if self._changed or len(self._nbs_list) == 0:
            for e in self.inclist():
                self._nbs_list.append(e.otherend(self))
            self._changed = False
        if not self._sorted:
            self._nbs_list = self.merge_sort_color(self, self._nbs_list)
        return self._nbs_list

    def deg(self):
        """
        Returns the degree of vertex <self>.
        """
        return len(self.nbs())

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

    def __init__(self,n=0,simple=False):
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

    def __getitem__(self,i):
        """
        Returns the <i>th vertex of the graph -- as given in the vertex list;
        this is not related to the vertex labels.
        """
        return self._V[i]

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

    def sortEdgesRec(self, list):
        if len(list) > 1:
            i = int((len(list) / 2))
            f = self.sortEdgesRec(list[:i])
            s = self.sortEdgesRec(list[i:])
            r = []
            fi = si = 0
            while fi < len(f) and si < len(s):
                if f[fi].tail().get_label() < s[si].tail().get_label() or f[fi].tail().get_label() == s[si].tail().get_label() and f[fi].head().get_label() < s[si].head().get_label():
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

    def sortEdges(self):
        self._EDouble = self.sortEdgesRec(self._EDouble)
        self.unsorted = False

    # uses binary algorithm to search for (first) elements in lists containing tupels
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

    def findFirstEdgeOfVertex(self, label):
        if self.unsorted == True:
            self.sortEdges()
        return self.binary_search_pairs(self._EDouble, label)


    def findedgeRec(self, u, v, max, min):
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
        if(max == min):
            return None
        if (u < v):
            high = v
            low = u
        else:
            high = u
            low = v
        e = self._EDouble
        b = max - min
        i = (b // 2) + min
        if e[i][1]==high and e[i][0]==low:
            return e[i]
        elif i == len(e) - 1:
            return None
        elif e[i][0] < low or e[i][1] < high:
            return self.findedgeRec(u, v, max, i)
        elif e[i][0] > low or e[i][1] > high:
            return self.findedgeRec(u, v, i, min)
        return None

    def findedge(self,u,v):
        if self.unsorted == True:
            self.sortEdges()
        return self.findedgeRec(u, v, len(self._EDouble), 0)

    def adj(self,u,v):
        """
        Returns True iff vertices <u> and <v> are adjacent.
        """
        if self.findedge(u,v) == None:
            return False
        else:
            return True

    def isdirected(self):
        """
        Returns False, because for now these graphs are always undirected.
        """
        return self._directed
		

