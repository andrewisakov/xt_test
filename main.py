#!/usr/bin/python3
from peewee import prefetch
import datetime
import models
import rules


class Order(object):
    def __init__(self, order_id: int=None):
        if (order_id is not None) and isinstance(order_id, int):
            self._order = models.Order.get(models.Order.id == order_id)
            self._order = prefetch(
                models.Order.select().where(models.Order.id == order_id),
                models.OrderItem.select(), models.Item.select(),
                models.ItemRules.select(), models.Rule.select())[0]
        else:
            self._order = models.Order.create()
        # print(self._order)

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

    def del_item(self, item_pos: int):
        return self._order[item_pos]

    def update_item(self, item):
        pass


if __name__ == '__main__':
    order = Order(1)
    print(f'id: {order.id}')
    print(f'items: {order.items}')
    print(f'owewr: {order.owner}')
    print(f'created: {order.created}')
