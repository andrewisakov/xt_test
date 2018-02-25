#!/usr/bin/python3
# import models


class Rule(object):
    __instances = {}  # {rule_id: <instance>}

    def __new__(cls, rule):
        if rule.id not in cls.__instances.keys():
            cls.__instances[rule.id] = object.__new__(cls, rule)
        return cls.__instances[rule.id]

    def __init__(self, rule):
        self.__receptors = set()

    def register(self, receptor):
        self.__receptors.add(receptor)

    def unregister(self, receptor):
        self.__receptors.discard(receptor)

    @property
    def result(self):
        for rec in self.__receptors:
            pass

    @property
    def receptors(self):
        return self.__receptors


class Receptor(object):
    __instances = {}  # {item_id: <instance>}

    def __new__(cls, item):
        if item.id not in cls.__instances.keys():
            cls.__instances[item.id] = object.__new__(cls, item)
        return cls.__instances[item.id]

    def __init__(self, item):
        self._rules = None
        self._receptor = item.id
        # TODO: Rule.add_receptor(item.id)

    def _put_item(self, item):
        # Установить состояние рецептора
        pass

    @classmethod
    def send_items(cls, items):
        for item in items:
            if item.id in cls.__instances.keys():
                cls.__instances[item.id]._put_item(item)

    def add_rule(self, rule):
        rule.register(self)


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


class ONE(object):
    def __init__(self):
        pass

