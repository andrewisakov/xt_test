#!/usr/bin/python3
import datetime
import models
import rules


class Order(object):
    def __init__(self, order_id: int = None):
        self._session = models.Session(models.engine)
        if order_id:
            self._order = self.session.query(models.Order).filter(
                models.Order.id == order_id).one_or_none()
        else:
            self._order = models.Order()
            self.commit(self._order)
        self._rules = set()
        self.add_items()

    @property
    def rules(self):
        return self._rules

    def commit(self, obj=None):
        if obj is not None:
            self.session.add(obj)
        self.session.commit()

    @property
    def session(self):
        return self._session

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

    def recalc(self):
        discounts = []
        for r in self._rules:
            items, quantity, discount = r.get_result()
            discounts.append(dict(items=items, quantity=quantity, discount=discount))
        return discounts

    def add_items(self, items=None):
        if isinstance(items, list):
            # print(f'add_items: {items}')
            for item in items:
                if isinstance(item, models.Item):
                    pass
        for order_item in self._order.items:
            print(f'Order.add_items order_item: {order_item}')
            self.add_item(order_item)

    def add_item(self, order_item, quantity=1):
        if isinstance(order_item, models.Item):
            """Новый item"""
            order_item = models.OrderItem(item, quantity=quantity)
            if order_item not in self._order.items:
                self._order.items.append(order_item)
                self.session.commit()

        for rule in order_item.item.rules:
            r = rules.Rule(rule.rule, self.id)
            item_related = list(
                [i for i in self._order.items if i.item_id == rule.item_related_id])
            item_related = item_related[0] if item_related else rule.item_related_id
            r.add_receptor(rule, order_item, item_related)
            self._rules.add(r)

        for rule in self._rules:
            rule.update_receptors(order_item)

    def del_item(self, order_item):
        # rules.Rule.del_receptor(self._order.id, order_item.item_id)
        # self._order.items.del(order_item)
        return order_item.item

    def __del__(self):
        # print(f'Order.__del__: {self.session}')
        self._session.close()

if __name__ == '__main__':
    order = Order()
    items = order.session.query(models.Item).filter(models.Item.name.in_(('A', 'B', 'L', 'D'))).all()
    items += order.session.query(models.Item).filter(models.Item.name.in_(('E', 'F', 'G',))).all()
    for item in items:
        order.add_item(item, 10)
    # print(f'add_items: {items}')
    # order.add_items(items)
    print(f'{order.items}')
    print(f'{order.recalc()}')
    # print(order.rules)
    # print(f'{item}')
    # order.add_item(item, quantity=10)
    # session.close()
