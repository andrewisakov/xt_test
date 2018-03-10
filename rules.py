#!/usr/bin/python3
import sys
from abc import abstractmethod
from settings import logger
import models


class Rule(object):
    """ Правило (автомат) """
    __instances = {}  # {(order_id, rule_id): <instance>}

    def __new__(cls, rule, order_id):
        # logger.debug(f'Rule.__new__.rule: {rule}')
        if (order_id, rule.id) not in cls.__instances.keys():
            _instance = object.__new__(cls)
            _instance.root = None
            _instance.tail = None
            _instance.rule = rule
            _instance._not_linked_cache = {}
            _instance._linked_cache = {}
            cls.__instances[(order_id, rule.id)] = _instance
        return cls.__instances[(order_id, rule.id)]

    def set_root(self, item_rule):
        if self.tail is None:
            # logger.debug(f'set_root: {item_rule.rule.condition}')
            if ':' in item_rule.rule.condition:
                self.root, self.tail = item_rule.rule.condition.split(':')
                self.root = getattr(sys.modules[__name__], self.root)()
                self.tail = getattr(sys.modules[__name__], self.tail)()
                self.tail.add_item(self.root)
            else:
                self.root = self.tail = getattr(
                    sys.modules[__name__], item_rule.rule.condition)()

    def remove_receptors(self, item: models.Item):
        """Удаление item из order"""
        if item.item_id not in self._not_linked_cache.keys():
            self._not_linked_cache[item.item_id] = set()
        if item in self._linked_cache.keys():
            for items in self._linked_cache[item]:
                items.del_item(item)
                items.add_item(item.item_id)
                self._not_linked_cache[item.item_id].add(items)
            del self._linked_cache[item]

    def update_receptors(self, order_item: models.Item):
        """Добавление item в order"""
        if order_item not in self._linked_cache:
            self._linked_cache[order_item] = set()
        if order_item.item_id in self._not_linked_cache.keys():
            for items in self._not_linked_cache[order_item.item_id]:
                # logger.debug(f'Rule.update_receptors: {items}')
                items.del_item(order_item.item_id)
                items.add_item(order_item)
                self._linked_cache[order_item].add(items)
                # logger.debug(f'update_receptor: {items}')
            del self._not_linked_cache[order_item.item_id]

    def put_not_linked_cache(self, item_related: int, _rule):
        # Кэш рецепторов для отсутствующих в ордере элементов
        if item_related not in self._not_linked_cache.keys():
            self._not_linked_cache[item_related] = set()
        self._not_linked_cache[item_related].add(_rule)

    def put_linked_cache(self, item_related: models.Item, _rule):
        if item_related not in self._linked_cache.keys():
            self._linked_cache[item_related] = set()
        self._linked_cache[item_related].add(_rule)

    def add_receptor(self, item_rule, order_item, item_related):
        self.set_root(item_rule)
        _rule = getattr(sys.modules[__name__], item_rule.condition)(
            trigger_value=item_rule.trigger_value)
        _rule.add_item(order_item)
        _rule.add_item(item_related)
        if isinstance(item_related, int):
            self.put_not_linked_cache(item_related, _rule)
        else:
            self.put_linked_cache(item_related, _rule)
        self.root.add_item(_rule)
        logger.debug(f'add_receptor: {type(_rule).__name__} {_rule._items}')

    def get_result(self):
        _result = self.tail.get_result()
        return _result + (self.rule.discount, ) if _result != set() else 0

    def __repr__(self):
        return f'{self.rule} {self.tail}'


class RuleClass(object):
    def __init__(self, trigger_value=1):
        self._items = []
        self._trigger_value = trigger_value
        # self._discount = discount

    def flatten(self, lis):
        """Given a list, possibly nested to any level, return it flattened."""
        new_lis = []
        for item in lis:
            if isinstance(item, list):
                new_lis.extend(self.flatten(item))
            else:
                new_lis.append(item)
        return new_lis

    def add_item(self, item):
        self._items.append(item)
        logger.debug(f'RuleClass.add_item: {item}')

    def del_item(self, item):
        self._items.remove(item)
        logger.debug(f'RuleClass.del_item: {item}')

    @property
    def items(self):
        return self._items

    @abstractmethod
    def get_result(self):
        pass

    def __repr__(self):
        return (f'{type(self).__name__}: {self._items}')


class ODD(RuleClass):
    def get_result(self):
        pass


class NOT(RuleClass):
    """Не равенство"""
    def get_result(self):
        logger.debug(f'{type(self).__name__} items: {self._items}')
        not_items = []
        for i in self._items:
            if isinstance(i, RuleClass):
                items = i.get_result()
                not_items.append(items[0])
            elif not isinstance(i, int):
                not_items.append(i)
        logger.debug(f'{type(self).__name__} not_items: {not_items}')
        if len(not_items) != 2:
            return [(), 0]
        else:
            if not_items[0] != not_items[1]:
                return [not_items[0], 1]
            else:
                return [(), 0]


class COUNT(RuleClass):
    def get_result(self):
        pass


class MAX(RuleClass):

    def get_result(self):
        max_items = []
        for i in self._items:
            if isinstance(i, RuleClass):
                logger.debug(f'{type(self).__name__} (2): {i}')
                items = i.get_result()
                logger.debug(f'{type(self).__name__} (3): {items}')
                min_items += items[0]
        max_trigger = max(
            max_items, key=lambda x: x.quantity) if max_items else None
        max_trigger = max_trigger.quantity if max_trigger else 0
        logger.debug(f'{type(self).__name__} max_trigger: {max_trigger}')
        return max_items, max_trigger


class MIN(RuleClass):
    def get_result(self):
        logger.debug(f'{type(self).__name__} (1): {self._items}')
        min_items = []
        for i in self._items:
            if isinstance(i, RuleClass):
                logger.debug(f'{type(self).__name__} (2): {i}')
                items = i.get_result()
                logger.debug(f'{type(self).__name__} (3): {items}')
                min_items += items[0]
        logger.debug(f'{type(self).__name__} (4): {min_items}')
        min_trigger = min(
            min_items, key=lambda x: x.quantity) if min_items else None
        min_trigger = min_trigger.quantity if min_trigger else 0
        logger.debug(f'{type(self).__name__} (5): {min_trigger}')
        return min_items, min_trigger


class ONE(RuleClass):
    """ Один или указанное в trigger_value """

    def get_result(self):
        logger.debug(f'{type(self).__name__} (1): {self._items}')
        one_items = []
        for i in self._items:
            if isinstance(i, RuleClass):
                ii = i.get_result()
                if ii and (ii[1] > 0):
                    one_items.append(ii[0])
            elif not isinstance(i, int):
                one_items.append(i)

        logger.debug(f'{type(self).__name__} one_items (4): {one_items}')

        return (one_items[0], self._trigger_value) if len(one_items) == self._trigger_value else ([], 0)


class AND(RuleClass):

    def get_result(self):
        logger.debug(f'{type(self).__name__} (1): {self._items} {len(self._items)}')
        and_items = []
        for i in self._items:
            if isinstance(i, RuleClass):
                ii = i.get_result()
                if ii and (ii[1] > 0):
                    and_items.append(ii[0])
            elif not isinstance(i, int):
                and_items.append(i)
        logger.debug(f'{type(self).__name__} (3): {and_items} {len(and_items)}')
        if len(and_items) == len(self._items):
            and_items = self.flatten(and_items)
            logger.debug(
                f'{type(self).__name__} (4): {and_items} {len(and_items)}')
            and_items = list(set(and_items))
            return (and_items, len(and_items))
        return ([], 0)


class OR(RuleClass):
    def get_result(self):
        logger.debug(f'{type(self).__name__}: {self._items}')
        or_items = []
        for i in self._items:
            if isinstance(i, RuleClass):
                ii = i.get_result()
                logger.debug(f'{type(self).__name__}: {ii}')
                if ii and (ii[1] > 0):
                    or_items.append(ii[0])
        logger.debug(f'{type(self).__name__}: {or_items}')
        # or_items = set(or_items)
        return (or_items, len(or_items))
