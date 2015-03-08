__author__ = 'Rob'

"""
Utility class for fast sort, zip and search functions
"""


# Merge sorts the list of number-tuples to the first or second element (indicated by index)
def sort_pairs_number(number_list, index):
    if len(number_list) > 1:
        i = int((len(number_list) / 2))
        f = sort_pairs_number(list[:i], index)
        s = sort_pairs_number(list[i:], index)
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
        return number_list


# Merge sorts the list of vertices sorts to label
def sort_vertex_label(vertices):
    if len(vertices) > 1:
        i = int((len(vertices) / 2))
        f = sort_vertex_label(vertices[:i])
        s = sort_vertex_label(vertices[i:])
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


# Merge sorts the list of vertices sorts to color
def sort_vertex_color(vertices):
    if len(vertices) > 1:
        i = int((len(vertices) / 2))
        f = sort_vertex_color(vertices[:i])
        s = sort_vertex_color(vertices[i:])
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


# Merge sorts the list of number-tuples to the first or second element (indicated by index)
def sort_pairs(tuple_list, index):
    if len(tuple_list) > 2:
        i = int((len(tuple_list) / 2))
        f = sort_pairs(tuple_list[:i], index)
        s = sort_pairs(tuple_list[i:], index)
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
        return tuple_list


# Adds one item to a sorted list of numbers
def zip_number(number_list, number, allow_duplicates=True):
    result = []
    if len(number_list) == 0:
        result.append(number)
        return result
    fi = search_number(number_list, number, -1)
    if fi != -1:
        result += number_list[:(fi + 1)]
    if allow_duplicates or fi == -1 or number_list[fi] != number:
        result.append(number)
    result += number_list[(fi + 1):]
    return result


# Adds one item to a sorted list of color, list of neighbors - tuples
# The list is sorted by the color of all neighbors
# all lists of neighbors must be sorted to color and of equal length
def zip_vertex_color_and_neighbors(color_and_neighbors_list, color_and_neighbor):
    result = []
    if len(color_and_neighbors_list) == 0:
        color_and_neighbors_list.append(color_and_neighbor)
        return result
    fi = search_vertex_color_and_neighbors(color_and_neighbors_list, color_and_neighbor[1], -1)
    if fi != -1:
        result += color_and_neighbors_list[:(fi + 1)]
    result.append(color_and_neighbor)
    result += color_and_neighbors_list[(fi + 1):]
    return result


# Adds one item to a sorted list of tuples
def zip_tuple(tuple_list, a_tuple, index):
    result = []
    if len(tuple_list) == 0:
        result.append(a_tuple)
        return result
    fi = search_pairs(tuple_list, a_tuple, index, -1)
    if fi != -1:
        result += tuple_list[:(fi + 1)]
    result.append(a_tuple)
    result += tuple_list[(fi + 1):]
    return result


# merges 'o.a.' transitive isomorphisms to one list: [0,1],[1,3] -> [0,1,3] and [0,1],[0,3] -> [0,1,3]
def zip_tuples_isomorphisms(list_old):
    list_new = []
    list_index = 0
    while len(list_old) > 0:
        root = list_old.pop(0)
        list_new.append([root[0], root[1]])
        while len(list_old) > 0 and list_old[0][0] == root[0]:
            list_new[list_index].append(list_old.pop(0)[1])
        len_of_list = len(list_new[list_index])
        i = 0
        added = False
        while i < len_of_list:
            start_index = search_pairs(list_old, list_new[list_index][i], 0, 0)
            if start_index == -1:
                i += 1
                continue
            # search forward
            dub = False
            while start_index < len(list_old) and list_old[start_index][0] == list_new[list_index][i]:
                new_item = list_old.pop(start_index)[1]
                dub = False
                for j in range(1, len(list_new[list_index])):
                    if list_new[list_index][j] == new_item:
                        dub = True
                        break
                if not dub:
                    list_new[list_index].append(new_item)
                    len_of_list += 1
                    added = True
            # search backward
            start_index -= 1
            while start_index >= 0 and list_old[start_index][0] == list_new[list_index][i]:
                new_item = list_old.pop(start_index)[1]
                for j in range(1, len(list_new[list_index])):
                    if list_new[list_index][j] == new_item:
                        dub = True
                        break
                if not dub:
                    list_new[list_index].append(new_item)
                    len_of_list += 1
                    added = True
                start_index -= 1
                i += 1
        if added:
            list_new[list_index].sort()
        list_index += 1
    return list_new


# Adds one item to a sorted list of numbers
# Action is whether to search for equal (0), smaller or equal (-1) or bigger or equal (1)
def search_number(number_list, number, action):
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
        if number_list[l] == number or (action == -1 and number_list[l] < number) \
                or (action == 1 and number_list[l] > number):
            return l
        elif action == -1 and l > 0:
            return l - 1
        elif action == 1 and l < len(number_list) - 1:
            return l + 1
        else:
            return -1
    else:
        return -1


# Binary search for label within the list of vertices.
def search_vertex_label(vertices, a_label):
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


# searches for a vertex with this color and neighbors
# Action is whether to search for equal (0), smaller or equal (-1) or bigger or equal (1)
def search_vertex_color_and_neighbors(color_and_neighbors_list, color_and_neighbor, action):
    if len(color_and_neighbors_list) > 0:
        l = 0
        h = len(color_and_neighbors_list) - 1
        comparison = compare_vertex_colors(color_and_neighbors_list[l][1], color_and_neighbor)
        while h - l > 0 and comparison != 0:
            m = int((l + h) / 2)
            comparison = compare_vertex_colors(color_and_neighbors_list[m][1], color_and_neighbor)
            if comparison == 0:
                l = m
            elif comparison == 1:
                h = m - 1
            else:
                l = m + 1
            comparison = compare_vertex_colors(color_and_neighbors_list[l][1], color_and_neighbor)
        if comparison == 0 or comparison == action:
            return l
        elif action == -1 and l > 0:
            return l - 1
        elif action == 1 and l < len(color_and_neighbors_list) - 1:
            return l + 1
        else:
            return -1
    else:
        return -1


# Binary search for the tuple where the first or second element (indicated by index) is equal (action == 0),
# smaller or equal (action == -1) or bigger or equal (action == 1).
def search_pairs(tuple_list, value, index, action):
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
        if tuple_list[l][index] == value or (action == -1 and tuple_list[l][index] < value) \
                or (action == 1 and tuple_list[l][index] > value):
            return l
        elif action == -1 and l > 0:
            return l - 1
        elif action == 1 and l < len(tuple_list) - 1:
            return l + 1
        else:
            return -1
    else:
        return -1


# Compares colors of the two lists of vertices which should already be sorted to color.
# Only tests whether they are equal or not
def compare_vertices_color_equal(l1, l2):
    if len(l1) != len(l2):
        return False
    for i in range(0, len(l1)):
        if l1[i].get_colornum() != l2[i].get_colornum():
            return False
    return True


# Compares colors of the two lists of vertices which should already be sorted to color
# Tests whether they are equal (0) or the first is smaller (1) or the second is smaller (-1)
def compare_vertex_colors(list1, list2):
    for i in range(0, len(list1)):
        if list1[i].get_colornum() < list2[i].get_colornum():
            return -1
        elif list1[i].get_colornum() == list2[i].get_colornum():
            continue
        else:
            return 1
    return 0  # it are duplicates