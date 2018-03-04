#!/usr/bin/python3
from abc import abstractmethod
from settings import logger
# import models


class Rule(object):
    """ Правило (нейрон) """
    __instances = {}  # {(order_id, rule_id): <instance>}

    def __new__(cls, rule, order_id):
        # print(f'Rule.__new__.rule: {rule}')
        if (order_id, rule.id) not in cls.__instances.keys():
            _instance = object.__new__(cls)
            _instance.root = None
            _instance.tail = None
            _instance.rule = rule
            _instance._not_linked_cache = {}
            cls.__instances[(order_id, rule.id)] = _instance
        return cls.__instances[(order_id, rule.id)]

    def set_root(self, item_rule):
        if self.tail is None:
            # print(f'set_root: {item_rule.rule.condition}')
            if ':' in item_rule.rule.condition:
                self.root, self.tail = item_rule.rule.condition.split(':')
                # self.root = RULES[self.root]()
                self.root = eval(self.root)()
                self.tail = eval(self.tail)()
                self.tail.add_item(self.root)
            else:
                self.root = self.tail = eval(item_rule.rule.condition)()

    def set_receptors(self, item):
        for items in self._not_linked_cache[item.item_id]:
            items.discard(item.item_id)
            items.add(item)
        del self._not_linked_cache[item.item_id]

    def put_not_linked_cache(self, item_related, _rule):
        # Кэш рецепторов для отсутствующих в ордере элементов
        if item_related not in self._not_linked_cache.keys():
            self._not_linked_cache[item_related] = set()
        self._not_linked_cache[item_related].add(_rule)

    def add_receptor(self, item_rule, order_item, item_related):
        self.set_root(item_rule)
        _rule = eval(item_rule.condition)(trigger_value=item_rule.trigger_value)  #, discount=item_rule.discount)
        _rule.add_item(order_item)
        _rule.add_item(item_related)
        if isinstance(item_related, int):
            self.put_not_linked_cache(item_related, _rule)
        self.root.add_item(_rule)
        print(f'add_receptor: {type(_rule).__name__} {_rule._items}')

    def get_result(self):
        # print(f'Rule.get_result: {self._not_linked_cache}')
        _result = self.tail.get_result()
        print(f'Rule.get_result (1): {_result}')
        return _result + (self.rule.discount, ) if _result != set() else 0


class RuleClass(object):
    def __init__(self, trigger_value=1):
        self._items = set()
        self._trigger_value = trigger_value
        # self._discount = discount

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
        max_items = []
        for i in self._items:
            if isinstance(i, RuleClass):
                max_items = set(
                    [item for item in i.get_result() if item is not None])
            else:
                max_items.add(i)
        max_trigger = max(max_items, key=lambda x: x.quantity) if max_items else []
        max_trigger = max_trigger.quantity if max_trigger else 0
        print(f'{type(self).__name__} max_trigger: {max_trigger}')
        return max_items, max_trigger


class MIN(RuleClass):
    def get_result(self):
        # min_item = None
        print(f'{type(self).__name__} (1): {self._items}')
        min_items = []
        for i in self._items:
            if isinstance(i, RuleClass):
                print(f'{type(self).__name__} (2): {i}')
                items = i.get_result()
                print(f'{type(self).__name__} (3): {items}')
                min_items += items[0]
                    # [item[0] for item in i.get_result() if item[0] != set()])
            # else:
            #     min_items.add(i)
        print(f'{type(self).__name__} (4): {min_items}')
        min_trigger = min(min_items, key=lambda x: x.quantity) if min_items else None
        min_trigger = min_trigger.quantity if min_trigger else 0
        print(f'{type(self).__name__} (5): {min_trigger}')
        return min_items, min_trigger


class ONE(RuleClass):
    """ Один или указанное в trigger_value """

    def get_result(self):
        print(f'{type(self).__name__}: {self._items}')
        # one_items = [(i.get_result() if isinstance(i, RuleClass) else i)
        #              for i in self._items if i != set()]
        one_items = []
        for i in self._items:
            print(f'{type(self).__name__} i: {i}')
            if isinstance(i, RuleClass):
                ii = i.get_result()
                if ii:
                    one_items.append(ii)
            # else:
            #     one_items.append()

        print(f'{type(self).__name__} one_items: {one_items}')
        # one_items = set(one_items)
        return (one_items, self._trigger_value) if len(one_items) == self._trigger_value else ([], 0)


class AND(RuleClass):

    def get_result(self):
        print(f'{type(self).__name__} (1): {self._items}')
        and_items = []
        for i in self._items:
            print(f'{type(self).__name__} (2): {i}')
            if not isinstance(i, int):
                and_items.append(i)
        and_items = set(and_items) if len(and_items) == len(self._items) else set()
        print(f'{type(self).__name__} (3): {and_items}')
        and_items = [item for item in and_items] if and_items != set() else []
        print(f'{type(self).__name__} (4): {and_items}')
        return (and_items, len(and_items)) if (len(and_items) == len(self._items)) else ([], 0)


class OR(RuleClass):
    def get_result(self):
        print(f'{type(self).__name__}: {self._items}')
        or_items = []
        for i in self._items:
            or_items = [(i.get_result() if isinstance(i, RuleClass) else i)
                        for i in self._items if i is not None]
        # or_items = set(or_items)
        return (or_items, len(or_items))
