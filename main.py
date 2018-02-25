#!/usr/bin/python3
import datetime
import models
import rules


class Rule(object):
    pass


class Order(object):
    def __init__(self, order: models.Order):
        self._order = order
        for order_item in order.items:
            print(order_item.item.rules)

    @property
    def id(self):
        return self._order.id

    @property
    def items(self):
        return self._order.items

    @property
    def owner(self):
        return self._order.user_id

    @property
    def created(self):
        return self._order.created

    def recalc_rules(self, item):
        pass

    def add_item(self, _item: models.Item):
        for item in self._order.items:
            # item.rules
            # TODO: Проверить вхождение _item.id в item.rules.item_related
            # TODO: Проверить вхождение item,id в _item.rules.item_related
            pass
        self._order.items.append(_item)
        self._order.save()

    # def del_item(self, item_pos: int):
    #     return self._order[item_pos]

    # def update_item(self, item):
    #     pass


if __name__ == '__main__':
    order = models.get_order(1)
    order = Order(order)
    item = models.get_items()[0]
    print(item)
    # order.items.append()

    print(f'id: {order.id}')
    print(f'items: {order.items}')
    print(f'owner: {order.owner}')
    print(f'created: {order.created}')
    print(f'item: {item}')
