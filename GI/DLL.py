__author__ = 'Rob'


class DoublyLinkedList(object):

    def __init__(self, first, last):
        self._first = first
        self._last = last

    def get_first(self):
        return self._first

    def set_first(self, first):
        self._first = first

    def get_last(self):
        return self._last

    def set_last(self, last):
        self._last = last

    def insert_first(self, new_item):
        if self._first is None:
            self._first = self._last = new_item
            new_item._prv = None
            new_item._nxt = None
        else:
            self.insert_before(self._first, new_item)

    def insert_last(self, new_item):
        if self._last is None:
            self.insert_first(new_item)
        else:
            self.insert_after(self._last, new_item)

    def insert_before(self, item, new_item):
        new_item._prv = item._prv
        new_item._nxt = item
        if item._prv is None:
            self._first = item
        else:
            item._prv._nxt = new_item
        item._prv = new_item

    def insert_after(self, item, new_item):
        new_item._prv = item
        new_item._nxt = item._nxt
        if item._nxt is None:
            self._last = item
        else:
            item._nxt._prv = new_item
        item._nxt = new_item

    def remove(self, item):
        if item._prv is None:
            self._first = item._nxt
        else:
            item._prv._nxt = item._nxt
        if item._nxt is None:
            self._last = item._prv
        else:
            item._nxt._prv = item._prv
        del item


class Item(object):

    def __init__(self, prv, nxt, value):
        self._prv = prv
        self._nxt = nxt
        self._value = value

    def get_prv(self):
        return self._prv

    def set_prv(self, prv):
        self._prv = prv

    def get_nxt(self):
        return self._nxt

    def set_nxt(self, nxt):
        self._nxt = nxt

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value