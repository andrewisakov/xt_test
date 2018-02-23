#!/usr/bin/python3
import datetime
from peewee import *
from settings import db


class BaseModel(Model):
    class Meta:
        database = db


class Orders(BaseModel):
    created = DateTimeField(default=datetime.datetime.now, index=True)
    # items = relationship('OrderItem', cascade='all, delete-orphan', backref='orders')

    def __repr__(self):
        return f'Order(id: {self.id}, created: {self.created}, items: {self.items})'


class Items(BaseModel):
    # id = Column(Integer, primary_key=True)
    name = CharField(null=False, index=True)
    price = DecimalField(max_digits=10, decimal_places=2)

    def __repr__(self):
        return f'Item(id: {self.id}, name: «{self.name}», price: {self.price}, rules: {self.item_rules})'


class Rules(BaseModel):
    description = CharField(unique=True, index=True)
    trigger_value = None
    result_value = None

    def __repr__(self):
        return f'{description}'


class ItemRules(BaseModel):
    rule = ForeignKeyField(Rules, index=True, backref='rule_conditions')
    item = ForeignKeyField(Items, index=True, backref='item_rules')
    item_related = IntegerField(index=True, null=True)
    condition = None

    def __repr__(self):
        return f'ItemRules(id: {self.id}, condition: {self.condition}, )'

    class Meta:
        database = db
        primary_key = CompositeKey('item', 'rule')


class OrderItems(BaseModel):
    order = ForeignKeyField(Orders, backref='items')
    item = ForeignKeyField(Items, primary_key=True)
    discount = DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = IntegerField(default=1)

    def __repr__(self):
        return f'OrderItem(order.id: {self.order.id}, item: {self.item}, quantity: {self.quantity}, discount: {self.discount})'


if __name__ == '__main__':
    db.connect()
    db.create_tables([Orders, OrderItems, Items, ItemRules, Rules], safe=True)
    new_items = (
        Items.create(name='A', price=10.91),
        Items.create(name='B', price=6.50),
        Items.create(name='C', price=8.99),
        Items.create(name='D', price=16.99)
    )
    order = Orders.create()
    # add three OrderItem associations to the Order and save
    order.items = tuple(OrderItems.create(item_id=item.id, order_id=order.id) for item in new_items)
    # order.items = (OrderItems.create(item_id=tshirt.id, order_id=order.id),
    #                OrderItems.create(item_id=mug.id, order_id=order.id),
    #                OrderItems.create(item_id=crowbar.id, quantity=10, order_id=order.id),
    #                OrderItems.create(item_id=hat.id, order_id=order.id),)
    # order.items.append(new_items)
    db.commit()
    print(order)
