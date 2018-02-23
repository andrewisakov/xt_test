#!/usr/bin/python3


class ODD(object):
    def __init__(self, items: tuple):
        pass


class AND(object):
    def __init__(self, items: tuple):
        pass


class NOT(object):
    def __init__(self):
        pass


class OR(object):
    def __init__(self, items: tuple, min_count=0, max_count=2):
        pass


class COUNT(object):
    def __init__(self, items: tuple, count: int=0):
        self._items = items
        self._count = count


class MAX(object):
    def __init__(self):
        pass


class MIN(object):
    def __init__(self):
        pass


class PAIRS(object):
    def __init__(self):
        pass
