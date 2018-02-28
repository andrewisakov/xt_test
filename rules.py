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
            _instance._not_linked_cache = {}
            cls.__instances[(order_id, rule.id)] = _instance
        return cls.__instances[(order_id, rule.id)]

    def add_receptor(self, item_rule, order_item, item_related):
        # print(f'add_receptor: {item_rule.condition} ({order_item.item_id}, {item_related.item_id})')
        if self.tail is None:
            print(f'add_receptor: {item_rule.rule.condition}')
            if ':' in item_rule.rule.condition:
                self.root, self.tail = item_rule.rule.condition.split(':')
                # self.root = RULES[self.root]()
                self.root = eval(self.root)()
                self.tail = eval(self.tail)()
                self.tail.add_item(self.root)
            else:
                # self.tail = self.root = RULES[item_rule.rule.condition]()
                self.root = self.tail = eval(item_rule.rule.condition)()
        # print(f'add_receptor.item_rule: {item_rule}')
        _rule = eval(item_rule.condition)()
        _rule.add_item(order_item)
        _rule.add_item(item_related)
        if isinstance(item_related, int):
            # print(f'add_receptor: {type(_rule).__name__} {item_related}')
            if item_related not in self._not_linked_cache.keys():
                self._not_linked_cache[item_related] = set()
            self._not_linked_cache[item_related].add(_rule)
        self.root.add_item(_rule)
        print(f'add_receptor: {type(_rule).__name__} {_rule._items}')

    @classmethod
    def set_receptor(cls, order_id, item):
        instances = [instance for k, instance in cls.__instances.items() if k[0] == order_id]
        print(order_id, item)

    def get_result(self):
        print(f'Rule.get_result: {self._not_linked_cache}')
        return self.tail.get_result()


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


class COUNT(RuleClass):
    def get_result(self):
        pass


class MAX(RuleClass):

    def get_result(self):
        items = set()
        for i in self._items:
            if isinstance(i, RuleClass):
                items = set(
                    [item for item in i.get_result() if item is not None])
            else:
                items.add(i)
        return max(items, key=lambda x: x.quantity)


class MIN(RuleClass):

    def get_result(self):
        # min_item = None
        print(f'{type(self).__name__}: {self._items}')
        min_items = set()
        for i in self._items:
            if isinstance(i, RuleClass):
                min_items = set(
                    [item for item in i.get_result() if item is not None])
            else:
                min_items.add(i)
        print(f'{type(self).__name__} min_items: {min_items}')
        return min(min_items, key=lambda x: x.quantity) if min_items else set()


class ONE(RuleClass):
    """ Один или указанное в trigger_value """

    def get_result(self):
        print(f'{type(self).__name__}: {self._items}')
        # one_items = [(i.get_result() if isinstance(i, RuleClass) else i)
        #              for i in self._items if i != set()]
        one_items = []
        for i in self._items:
            print(f'{type(self).__name__} i: {i}')
            if i != set():
                if isinstance(i, RuleClass):
                    ii = i.get_result()
                    if ii != set():
                        one_items.append(i.get_result())
                # else:
                #     one_items.append()

        print(f'{type(self).__name__} one_items: {one_items}')
        one_items = set(one_items)
        return one_items if len(one_items) == self._trigger_value else set()


class AND(RuleClass):

    def get_result(self):
        print(f'{type(self).__name__}: {self._items}')
        and_items = set()
        for i in self._items:
            if not isinstance(i, int):
                and_items.add(i)
        return and_items if len(and_items) == len(self._items) else set()


class OR(RuleClass):
    def get_result(self):
        print(f'{type(self).__name__}: {self._items}')
        or_items = []
        for i in self._items:
            or_items = [(i.get_result() if isinstance(i, RuleClass) else i)
                        for i in self._items if i is not None]
        or_items = set(or_items)
        return or_items
