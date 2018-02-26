#!/usr/bin/python3
# import models


class Rule(object):
    """ Правило (нейрон) """
    __instances = {}  # {rule_id: <instance>}

    def __new__(cls, rule):
        if rule.id not in cls.__instances.keys():
            cls.__instances[rule.id] = object.__new__(cls, rule)
        return cls.__instances[rule.id]

    def __init__(self, rule):
        print(f'Rule: {rule}')
        self._rules = set()

    def add_receptor(self, item_rule, items):
        print(f'{item_rule} {items})

    def get_result(self):
        pass


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
                items.add([for item in i.get_result() if item is not None] if isinstance(i, RuleClass) else i)
        return max(items, key=lamda x: x.quantity)


class MIN(RuleClass):
    def get_result(self):
        # min_item = None
        items = set()
        for i in self._items:
            if i is not None:
                items.add([for item in i.get_result() if item is not None] if isinstance(i, RuleClass) else i)
        # items = min(items, key=lamda x: x.quantity)
        return min(items, key=lamda x: x.quantity)


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
