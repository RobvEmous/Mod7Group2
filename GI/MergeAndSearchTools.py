__author__ = 'Rob'

"""
Utility class for fast sort, zip and search functions
"""


# Merge sorts the list of number-tuples to the first or second element (indicated by index)
def sort_number(number_list):
    if len(number_list) > 1:
        i = int((len(number_list) / 2))
        f = sort_number(number_list[:i])
        s = sort_number(number_list[i:])
        r = []
        fi = si = 0
        while fi < len(f) and si < len(s):
            if f[fi] <= s[si]:
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

# Merge sorts the list of number-tuples to the first or second element (indicated by index)
def sort_tuple_list(tuple_list):
    if len(tuple_list) > 1:
        i = int((len(tuple_list) / 2))
        f = sort_tuple_list(tuple_list[:i])
        s = sort_tuple_list(tuple_list[i:])
        r = []
        fi = si = 0
        while fi < len(f) and si < len(s):
            #if f[fi] <= s[si]:
            if compare_vertex_label(f[fi][1], s[si][1]) < 1:
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


# Merge sorts the list of number-tuples to the first or second element (indicated by index)
def sort_pairs_number(number_list, index):
    if len(number_list) > 1:
        i = int((len(number_list) / 2))
        f = sort_pairs_number(number_list[:i], index)
        s = sort_pairs_number(number_list[i:], index)
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


# Merge sorts the list of vertices to label
def sort_vertex_label_rem_dups(vertices):
    if len(vertices) > 1:
        i = int((len(vertices) / 2))
        f = sort_vertex_label_rem_dups(vertices[:i])
        s = sort_vertex_label_rem_dups(vertices[i:])
        r = []
        fi = si = 0
        while fi < len(f) and si < len(s):
            if f[fi].get_label() <= s[si].get_label():
                r.append(f[fi])
                if f[fi].get_label() == s[si].get_label():
                    si += 1
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

# Merge sorts the list of vertices to label
def sort_vertex_label(vertices):
    if len(vertices) > 1:
        i = int((len(vertices) / 2))
        f = sort_vertex_label(vertices[:i])
        s = sort_vertex_label(vertices[i:])
        r = []
        fi = si = 0
        while fi < len(f) and si < len(s):
            if f[fi].get_label() <= s[si].get_label():
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
def sort_vertex_color_and_changed(vertices):
    if len(vertices) > 1:
        i = int((len(vertices) / 2))
        f = sort_vertex_color_and_changed(vertices[:i])
        s = sort_vertex_color_and_changed(vertices[i:])
        r = []
        fi = si = 0
        while fi < len(f) and si < len(s):
            if f[fi].is_nbs_color_changed() and s[si].is_nbs_color_changed():
                if f[fi].get_colornum() <= s[si].get_colornum():
                    r.append(f[fi])
                    fi += 1
                else:
                    r.append(s[si])
                    si += 1
            elif s[si].is_nbs_color_changed():
                r.append(s[si])
                si += 1
            else:
                r.append(f[fi])
                fi += 1
        if fi < len(f):
            r += f[fi:]
        elif si < len(s):
            r += s[si:]
        return r
    else:
        return vertices


# Merge sorts the list of vertices sorts to color
def sort_vertex_color_and_nbs_to_label(vertices):
    if len(vertices) > 1:
        i = int((len(vertices) / 2))
        f = sort_vertex_color_and_nbs_to_label(vertices[:i])
        s = sort_vertex_color_and_nbs_to_label(vertices[i:])
        r = []
        fi = si = 0
        while fi < len(f) and si < len(s):
            if f[fi].get_colornum() < s[si].get_colornum():
                r.append(f[fi])
                fi += 1
            elif f[fi].get_colornum() == s[si].get_colornum():
                comparison = compare_vertex_label(f[fi].nbs_sorted_to_label(), s[si].nbs_sorted_to_label())
                if comparison <= 0:
                    r.append(f[fi])
                    fi += 1
                else:
                    r.append(s[si])
                    si += 1
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
            if f[fi].get_colornum() <= s[si].get_colornum():
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
    if len(tuple_list) >= 2:
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


# Merge sorts the list of list-tuples to their length (small to big) element (indicated by index)
def sort_pairs_to_len(tuple_list):
    if len(tuple_list) >= 2:
        i = int((len(tuple_list) / 2))
        f = sort_pairs_to_len(tuple_list[:i])
        s = sort_pairs_to_len(tuple_list[i:])
        r = []
        fi = si = 0
        while fi < len(f) and si < len(s):
            if len(f[fi]) <= len(s[si]):
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
        return result, 0
    fi = search_pairs(tuple_list, a_tuple[index], index, -1)
    if fi != -1:
        result += tuple_list[:(fi + 1)]
    index = len(result)
    result.append(a_tuple)
    result += tuple_list[(fi + 1):]
    return result, index


# Adds one item to a sorted list of nodes (to color)
def zip_nodes(vertices_list, a_vertex):
    result = []
    if len(vertices_list) == 0:
        result.append(a_vertex)
        return result
    fi = search_vertex_color(vertices_list, a_vertex.get_colornum(), -1)
    if fi != -1:
        result += vertices_list[:(fi + 1)]
    result.append(a_vertex)
    result += vertices_list[(fi + 1):]
    return result


# Adds one item to a sorted list of nodes (to label)
def zip_nodes_label(vertices_list, a_vertex):
    result = []
    if len(vertices_list) == 0:
        result.append(a_vertex)
        return result
    fi = search_vertex_color(vertices_list, a_vertex.get_label(), -1)
    if fi != -1:
        result += vertices_list[:(fi + 1)]
    result.append(a_vertex)
    result += vertices_list[(fi + 1):]
    return result


def blow_tuples_isomorphisms_all(zipped_tuples):
    print(zipped_tuples)
    list_new = []
    for i in range(0, len(zipped_tuples)):
        list_new.append([(zipped_tuples[i][0][0], zipped_tuples[i][0][1])])
        for j in range(1, len(zipped_tuples[i])):
            list_new[i].append((zipped_tuples[i][j][0], zipped_tuples[i][j][1]))
        for j in range(0, len(zipped_tuples[i])):
            for k in range(j + 1, len(zipped_tuples[i])):
                list_new[i].append((zipped_tuples[i][j][1], zipped_tuples[i][k][1]))
        sort_pairs(list_new[i], 0)
    return list_new

def blow_tuples_isomorphisms_list(zipped_tuples):
    list_new = []
    for i in range(1, len(zipped_tuples)):
        list_new.append((zipped_tuples[0], zipped_tuples[i]))
    return list_new

def blow_tuples_isomorphisms_list_of_list(zipped_tuples):
    list_new = []
    for i in range(0, len(zipped_tuples)):
        for j in range(1, len(zipped_tuples[i])):
            list_new.append((zipped_tuples[i][0], zipped_tuples[i][j]))
    return list_new


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


# Binary search for (all) color(s) within the list of vertices.
def search_vertex_color_dup(vertices, color):
    l = 0
    h = len(vertices) - 1
    while h - l > 0 and vertices[l].get_colornum() != color:
        m = int((l + h) / 2)
        if vertices[m].get_colornum() == color:
            l = m
        elif vertices[m].get_colornum() < color:
            l = m + 1
        else:
            h = m - 1
    if vertices[l].get_colornum() == color:
        new_vertices_old_indices = [l]
        if l > 0:
            index = l - 1
            while True:
                curr_color = vertices[index].get_colornum()
                if curr_color == color:
                    new_vertices_old_indices.append(index)
                    if index < len(vertices) - 1:
                        index -= 1
                    else:
                        break
                else:
                    break
        if l < len(vertices) - 1:
            index = l + 1
            while True:
                curr_color = vertices[index].get_colornum()
                if curr_color == color:
                    new_vertices_old_indices.append(index)
                    if index < len(vertices) - 1:
                        index += 1
                    else:
                        break
                else:
                    break
        return new_vertices_old_indices
    else:
        return []

# searches for a vertex with this color
# Action is whether to search for equal (0), smaller or equal (-1) or bigger or equal (1)
def search_vertex_color(vertices, color, action):
    if len(vertices) > 0:
        l = 0
        h = len(vertices) - 1
        while h - l > 0 and vertices[l].get_colornum() != color:
            m = int((l + h) / 2)
            if vertices[m].get_colornum() == color:
                l = m
            elif vertices[m].get_colornum() < color:
                l = m + 1
            else:
                h = m - 1
        if vertices[l].get_colornum() == color or (action == -1 and vertices[l].get_colornum() < color) \
                or (action == 1 and vertices[l].get_colornum() > color):
            return l
        elif action == -1 and l > 0:
            return l - 1
        elif action == 1 and l < len(vertices) - 1:
            return l + 1
        else:
            return -1
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
            comparison = compare_vertex_colors(color_and_neighbors_list[m][1], color_and_neighbor) # this was the nasty bug
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
    if len(list1) != len(list2):
        raise IndexError("problem!")
    for i in range(0, len(list1)):
        if list1[i].get_colornum() < list2[i].get_colornum():
            return -1
        if list1[i].get_colornum() == list2[i].get_colornum():
            continue
        else:
            return 1
    return 0  # they are duplicates

def compare_vertex_label(list1, list2):
    if len(list1) != len(list2):
        raise IndexError("problem!")
    for i in range(0, len(list1)):
        if list1[i].get_label() < list2[i].get_label():
            return -1
        elif list1[i].get_label() == list2[i].get_label():
            continue
        else:
            return 1
    return 0  # they are duplicates


def compare_vertex_label_equal(list1, list2):
    if len(list1) != len(list2):
        raise IndexError("problem!")
    for i in range(0, len(list1)):
        if list1[i].get_label() == list2[i].get_label():
            continue
        else:
            return 0
    return 1  # they are duplicates


def copy_colors_all(vertices_lists):
    colors_list = []
    for entry in vertices_lists:
        colors_list.append(copy_colors(entry))
    return colors_list


def copy_colors(vertices_list):
    colors = []
    for entry in vertices_list:
        colors.append((entry.get_label(), entry.get_colornum()))
    return sort_pairs(colors, 0)


def restore_colors(vertices_list, colors_list):
    vertices_list = sort_vertex_label(vertices_list)
    for entry_index, entry in enumerate(vertices_list):
        entry.set_colornum(colors_list[entry_index][1])
    vertices_list = sort_vertex_color(vertices_list)
    return vertices_list


def copy_graph_info(graph_info_list):
    new_list = []
    for entry in graph_info_list:
        new_list.append(entry.get_copy())
    return new_list


def gcd( a, b):
    while (b != 0):
        t = b;
        b = a % b;
        a = t;
    return a;


def lcm(a, b):
    return (a * b / gcd(a, b))


def lcmm(args):
    if(len(args) == 2):
        return lcm(args[0], args[1])
    else:
        arg0 = args[0]
        args.pop(0)
        return lcm(arg0, lcmm(args))

