#!/usr/bin/python3
from abc import abstractmethod
from settings import logger
# import models


class Rule(object):
    """ Правило (нейрон) """
    __instances = {}  # {(order_id, rule_id): <instance>}

    def __new__(cls, rule, order_id):
        if (order_id, rule.id) not in cls.__instances.keys():
            _instance = object.__new__(cls)
            _instance.root = None
            _instance.tail = None
            cls.__instances[(order_id, rule.id)] = _instance
        return cls.__instances[(order_id, rule.id)]

    def __init__(self, *args, **kwargs):
        pass

    def add_receptor(self, item_rule, order_item, item_related):
        print(f'add_receptor: {item_rule} ({order_item}, {item_related})')
        if self.root is None:
            pass

    def get_result(self):
        return self.tail


class RuleClass(object):
    def __init__(self, trigger_value=1):
        self._items = set()
        self._trigger_value = trigger_value

    def add_item(self, item):
        self._items.add(item)

    def del_item(self, item):
        self._items.discard(item)

    @property
    def items(self):
        return self._items

    @abstractmethod
    def get_result(self):
        pass


class ODD(RuleClass):
    def get_result(self):
        pass


class NOT(RuleClass):
    def get_result(self):
        pass


class OR(RuleClass):
    def get_result(self):
        pass


class COUNT(RuleClass):
    def get_result(self):
        pass


class MAX(RuleClass):
    def get_result(self):
        items = set()
        for i in self._items:
            if i is not None:
                items.add([item for item in i.get_result() if item is not None] if isinstance(i, RuleClass) else i)
        return max(items, key=lambda x: x.quantity)


class MIN(RuleClass):
    def get_result(self):
        # min_item = None
        items = set()
        for i in self._items:
            if i is not None:
                items.add([item for item in i.get_result() if item is not None] if isinstance(i, RuleClass) else i)
        # items = min(items, key=lamda x: x.quantity)
        return min(items, key=lambda x: x.quantity)


class ONE(RuleClass):
    """ Один или указанное в trigger_value """
    def get_result(self):
        one_items = set([(i.get_result() if isinstance(i, RuleClass) else i)
                         for i in self._items if i is not None])
        return one_items if len(one_items) == self._trigger_value else set()


class AND(RuleClass):
    def get_result(self):
        if None not in self._items:
            return self._items
        return set()
