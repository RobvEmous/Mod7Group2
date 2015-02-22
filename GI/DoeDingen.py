import pdb

from graphIO import writeDOT, loadgraph

def doeAlles():
    # laad de grafen
    num = 6
    vertices = 7680
    print('Finding Graph Isomorphisms between', num, 'graphs with', vertices, 'vertices.')
    print()
    print('- Loading graphs...')
    L = loadgraph('Graphs/crefBM_' + str(num) + '_' + str(vertices) + '.grl',readlist=True)
    graph_list = L[0]
    # kleur alle nodes naar aanleiding van hun degree (aantal buren)
    # Hierna wordt de lijst van nodes gesorteerd op kleur
    isomorphic = []
    maxDeg = []
    sortedVertices = [[]]*len(graph_list)
    print('- Initial coloring...')
    for i in range(0, len(graph_list)):
        print(i, 'of', len(graph_list), end=' ')
        maxDeg.append(0)
        for j in range(0, len(graph_list[i].V())):
            currDeg = graph_list[i].V()[j].deg()
            graph_list[i].V()[j].colornum = currDeg
            if currDeg > maxDeg[i]:
                maxDeg[i] = currDeg
        # sort it to color
        sortedVertices[i] = merge_sort_color(graph_list[i].V())
        writeDOT(graph_list[i],('Results/colorful_' + str(i) + '.dot'))
        print(' max degree =', maxDeg[i])
    # update iso file
    for i in range(0, len(maxDeg)):
        for j in range(i + 1, len(maxDeg)):
            if maxDeg[i] == maxDeg[j]:
                isomorphic.append((i, j))
    converged = False
    hasDupColors = [False]*len(graph_list)
    iteration_counter = 0
    print('- Recursive coloring...')
    while not converged:
        print('Iteration ', iteration_counter)
        converged = True
        for i in range(0, len(graph_list)):
            if binary_search_pairs(isomorphic, i, 0) == -1 and binary_search_pairs(merge_sort_pairs_second(isomorphic), i, 1) == -1:
                print(i, 'of', len(graph_list), ' is not isomorphic and is skipped')
                continue
            print(i, 'of', len(graph_list), end=' ')
            isConverged, hasDupColors[i], maxDeg[i] = color_Nbss(sortedVertices[i], maxDeg[i])
            if not isConverged:
                converged = False
            # update colors of nodes in graph
            sortedToLabelVertices = merge_sort_label(sortedVertices[i])
            for j in range(0, len(sortedToLabelVertices)):
                graph_list[i].V()[j].colornum = sortedToLabelVertices[graph_list[i].V()[j].get_label()].colornum
            sortedVertices[i] = merge_sort_color(graph_list[i].V())
            writeDOT(graph_list[i],('Results/colorfulIt_' + str(i) + '_' + str(iteration_counter) + '.dot'))
            print(' num of unique colors =', maxDeg[i], '; converged =', isConverged, '; all colors unique =', not hasDupColors[i])
        # update isomorphism
        for entry in isomorphic[:]:
            if maxDeg[entry[0]] != maxDeg[entry[1]]:
                isomorphic.remove(entry)
        iteration_counter += 1
    print('Graphs have converged after', iteration_counter, 'iterations.')
    print('- Matching graphs...')
    isomorphic = mergeIsos(isomorphic)
    for entry in isomorphic:
        nonDubs = 0
        for i in range(0, len(entry)):
            if hasDupColors[entry[i]]:
                print('Dups found in', entry[i], ': problem for now')
            else:
                nonDubs += 1
        if nonDubs >= 2:
            print('Isomorphism found between: ', end='')
            for i in range(0, len(entry)):
                if not hasDupColors[entry[i]]:
                    if i == 0:
                        print(entry[i], end='')
                    elif i < len(entry) - 1:
                        print(',', entry[i], end='')
                    else:
                        print(' and', entry[i])

# merges 'o.a.' transitive isomorphisms to one tuple: (0,1),(1,3) -> (0,1,3) and (0,1),(0,3) -> (0,1,3)
def mergeIsos(oldList):
    newList = []
    listIndex = 0;
    while len(oldList) > 0:
        root = oldList.pop(0)
        newList.append([root[0], root[1]])
        while len(oldList) > 0 and oldList[0][0] == root[0]:
            newList[listIndex].append(oldList.pop(0)[1])
        newList[listIndex].sort()
        added = False
        for i in range(1, len(newList[listIndex])):
            startIndex = binary_search_pairs(oldList, newList[listIndex][i], 0)
            if startIndex == -1:
                continue
            added = True
            # search forward
            while startIndex < len(oldList) and oldList[startIndex][0] == newList[listIndex][i]:
                newItem = oldList.pop(startIndex)[1]
                dub = False
                for j in range(i + 1, len(newList[listIndex])):
                    if newList[listIndex][j] == newItem:
                        dub = True
                        break
                if not dub:
                    newList[listIndex].append(newItem)
            # search backward
            startIndex -= 1
            while startIndex >= 0 and oldList[startIndex][0] == newList[listIndex][i]:
                newItem = oldList.pop(startIndex)[1]
                for j in range(i + 1, len(newList[listIndex])):
                    if newList[listIndex][j] == newItem:
                        dub = True
                        break
                if not dub:
                    newList[listIndex].append(newItem)
                startIndex -= 1
        if added:
            newList[listIndex].sort()
        listIndex += 1
    return newList

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
                        sortedVertices[i].colornum = colorChangedNeigbors[j][0]
                        changed = True
                        converged = False
            if not changed and not compareLists(startNbss, currNbs):
                maxDeg += 1
                sortedVertices[i].colornum = maxDeg
                colorChangedNeigbors.append((sortedVertices[i].colornum, currNbs))
                converged = False
        else:
            startColor = sortedVertices[i].colornum
            startNbss = currNbs
            colorChangedNodes = []
    return converged, hasDupColors, maxDeg

# uses binary algorithm to search for (first) elements in lists containing tupels
def binary_search_pairs(list, value, index):
    if len(list) > 0:
        l = 0
        h = len(list) - 1
        while h - l > 0 and list[l][index] != value:
            m = int((l + h) / 2)
            if list[m][index] == value:
                l = m
            elif list[m][index] < value:
                l = m + 1
            else:
                h = m - 1
        if list[l][index] == value:
            return l
        else:
            return -1
    else:
        return -1

# sorts to color
def merge_sort_pairs_second(list):
    if len(list) > 1:
        i = int((len(list) / 2))
        f = merge_sort_pairs_second(list[:i])
        s = merge_sort_pairs_second(list[i:])
        r = []
        fi = si = 0
        while fi < len(f) and si < len(s):
            if f[fi][1] < s[si][1] or f[fi][1] == s[si][1] and f[fi][0] < s[si][0]:
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