import pdb

from graphIO import writeDOT, loadgraph

def doeAlles():
    # laad de grafen
    L = loadgraph('Graphs/crefBM_4_4098.grl',readlist=True)
    graph_list = L[0]
    # kleur alle nodes naar aanleiding van hun degree (aantal buren)
    # Optimalisaties:   - alle nodes met degree 1 worden verwijderd
    #                   - alle nodes met degree 2 worden verwijderd én
    #                     de buren worden rechtstreeks aan elkaar geknoopt als dat nog niet zo was
    # Hierna wordt de lijst van nodes gesorteerd op kleur
    maxDeg = []
    sortedVertices = [[]]*len(graph_list)
    print('- Initial coloring...')
    for i in range(0, len(graph_list)):
        print(i, ' of ', len(graph_list))
        maxDeg.append(0)
        for j in range(0, len(graph_list[i].V())):
            currDeg = graph_list[i].V()[j].deg()
            graph_list[i].V()[j].colornum = currDeg
            if currDeg > maxDeg[i]:
                maxDeg[i] = currDeg
        # sort it to color
        sortedVertices[i] = merge_sort_color(graph_list[i].V())
        writeDOT(graph_list[i],('Results/colorful_' + str(i) + '.dot'))

    converged = False
    hasDupColors = []
    iteration_counter = 0
    print('- Recursive coloring...')
    while not converged:
        print('Iteration ', iteration_counter)
        for i in range(0, len(graph_list)):
            print(i, ' of ', len(graph_list))
            converged, hasDups, maxDeg[i] = color_Nbss(sortedVertices[i], maxDeg[i])
            hasDupColors.append(hasDups)
            # update colors of nodes in graph
            sortedToLabelVertices = merge_sort_label(sortedVertices[i])
            for j in range(0, len(sortedToLabelVertices)):
                graph_list[i].V()[j].colornum = sortedToLabelVertices[graph_list[i].V()[j]._label].colornum
            sortedVertices[i] = merge_sort_color(graph_list[i].V())
            writeDOT(graph_list[i],('Results/colorfulIt_' + str(i) + '_' + str(iteration_counter) + '.dot'))
        iteration_counter += 1
    print('- Matching graphs...')
    for i in range(0, len(graph_list)):
        if hasDupColors[i]:
            print('Dups found in ', i, ' : problem for now')
        else:
            for j in range(i + 1, len(graph_list)):
                if maxDeg[i] == maxDeg[j]:
                    print('Iso found:   ', i, ' and ', j)

def color_Nbss(sortedVertices, maxDeg):
    converged = True
    hasDupColors = False

    startColor = sortedVertices[0].colornum
    startNbss = merge_sort_color(sortedVertices[0].nbs())
    colorChangedNeigbors = []
    for i in range(1, len(sortedVertices)):
        currNbs = merge_sort_color(sortedVertices[i].nbs())
        if sortedVertices[i].colornum == startColor:
            hasDupColors = True
            changed = False
            if len(colorChangedNeigbors) > 0:
                for j in range(0, len(colorChangedNeigbors)):
                    if compareLists(colorChangedNeigbors[j][1], currNbs):
                        sortedVertices[i].colornum = colorChangedNeigbors[j][0].colornum
                        changed = True
                        converged = False
            if not changed and not compareLists(startNbss, currNbs):
                maxDeg += 1
                sortedVertices[i].colornum = maxDeg
                colorChangedNeigbors.append((sortedVertices[i], currNbs))
                converged = False
        else:
            startColor = sortedVertices[i].colornum
            startNbss = currNbs
            colorChangedNodes = []
    return converged, hasDupColors, maxDeg


# sorts to color
def merge_sort_color(vertices):
    if len(vertices) > 1:
        i = int((len(vertices) / 2))
        f = merge_sort_color(vertices[:i])
        s = merge_sort_color(vertices[i:])
        r = []
        fi = si = 0
        while fi < len(f) and si < len(s):
            if f[fi].colornum < s[si].colornum:
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

# sorts to label
def merge_sort_label(vertices):
    if len(vertices) > 1:
        i = int((len(vertices) / 2))
        f = merge_sort_label(vertices[:i])
        s = merge_sort_label(vertices[i:])
        r = []
        fi = si = 0
        while fi < len(f) and si < len(s):
            if f[fi]._label < s[si]._label:
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

#uses binary algorithm to search for elements in a list
def binaryLabelSearch(list, label):
    l = 0
    h = len(list) - 1
    while h - l > 0 and list[l]._label != label:
        m = int((l + h) / 2)
        if list[m]._label == label:
            l = m
        elif list[m]._label < label:
            l = m + 1
        else:
            h = m - 1
    if list[l]._label == label:
        return l
    else:
        return -1

def compareLists(l1, l2):
    if len(l1) != len(l2):
        return False
    for i in range(0, len(l1)):
        if l1[i].colornum != l2[i].colornum:
            return False
    return True

doeAlles()