#!/usr/bin/python3
import datetime
from peewee import *
from settings import db


conditions = ('AND', 'NOT', 'OR', 'COUNT', 'MAX', 'MIN', 'PAIRS', 'ODD')


class BaseModel(Model):
    class Meta:
        database = db


class Order(BaseModel):
    created = DateTimeField(default=datetime.datetime.now, index=True)
    user_id = IntegerField(default=1)
    # items = relationship('OrderItem', cascade='all, delete-orphan', backref='orders')

    def __repr__(self):
        return f'Order(id: {self.id}, created: {self.created}, items: {self.items})'

    class Meta:
        db_table = 'orders'


class Item(BaseModel):
    # id = Column(Integer, primary_key=True)
    name = CharField(null=False, index=True, unique=True)
    price = DecimalField(max_digits=10, decimal_places=2)

    def __repr__(self):
        return f'Item(id: {self.id}, name: «{self.name}», price: {self.price}, rules: {self.item_rules})'

    class Meta:
        db_table = 'items'


class Rule(BaseModel):
    condition = CharField()  # 'OR[:[min_trigger:int], max_trigger:int]]'
    trigger_value = IntegerField(default=0)
    discount = DecimalField(default=0)
    description = CharField(unique=True, index=True)

    def __repr__(self):
        return (f'condition: {self.condition}, trigger_value: {self.trigger_value}, discount: {self.discount}, {description}')

    class Meta:
        db_table = 'rules'


class ItemRules(BaseModel):
    """if item_id == 0 - неразборчивое правило"""
    item = ForeignKeyField(Item, index=True, backref='item_rules', on_delete='CASCADE')
    item_related = IntegerField(index=True)
    condition = CharField(null=True)  # 'OR[:[min_trigger:int], max_trigger:int]]'
    trigger_value = IntegerField(default=0)
    result_value = IntegerField(default=0)
    as_boolean = BooleanField(default=False)
    rule = ForeignKeyField(Rule, index=True, backref='rule_conditions')

    def __repr__(self):
        return f'ItemRules(id: {self.id}, condition: {self.condition}, item: {self.item}, item_related: {self.item_related})'

    class Meta:
        database = db
        primary_key = CompositeKey('item', 'rule', 'item_related')
        db_table = 'item_rules'


class OrderItem(BaseModel):
    order = ForeignKeyField(Order, backref='items', on_delete='CASCADE')
    item = ForeignKeyField(Item)
    # discount = DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = IntegerField(default=1)

    def __repr__(self):
        return f'OrderItem(order.id: {self.order.id}, item: {self.item}, quantity: {self.quantity})'

    class Meta:
        database = db
        primary_key = CompositeKey('order', 'item')
        db_table = 'order_items'


if __name__ == '__main__':
    db.connect()
    db.drop_tables([Order, OrderItem, Item, ItemRules, Rule], safe=True)
    db.create_tables([Order, OrderItem, Item, ItemRules, Rule], safe=True)
    new_items = [Item.create(name=chr(r), price=10.91)
                 for r in range(ord('A'), ord('Z') + 1)]
    order = Order.create()
    order.items = tuple(OrderItem.create(
        item_id=item.id, order_id=order.id) for item in new_items)
    order = Order.create()
    order.items = tuple(OrderItem.create(
        item_id=item.id, order_id=order.id) for item in new_items)
    db.commit()
    # print(1, type(order))
    items_rules = prefetch(Item.select().where((Item.name == 'A') | (
        Item.name == 'B')), ItemRules.select(), Rule.select())
    items = [item for item in items_rules]
    item_a, item_b = items
    print(item_a, item_b)
    rule = Rule.create(description='A&B', condition='MIN')
    rule_a = ItemRules.create(item=item_a, item_related=item_b.id, rule=rule, condition='AND')
    item_a.item_rules.append(rule_a)
    # item_a.save()
    # rule = Rules.create(description='B&A', condition='MIN')
    # rule_b = ItemRules.create(item=item_b, item_related=item_a.id, rule=rule)
    # item_b.item_rules.append(rule_b)
    # item_b.save()
    db.commit()
    # orders_items = prefetch(Orders.select().where(Orders.id == 1),
    #                         OrderItems.select(),
    #                         Items.select(),
    #                         ItemRules.select())
    print(item_a, item_b)
    print(order)
    Order.delete().where(Order.id == order.id).execute()
    db.commit()
