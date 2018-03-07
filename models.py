#!/usr/bin/python3

import datetime
from decimal import Decimal as D
import sqlalchemy.types as types
from sqlalchemy import (Column, DateTime, String, Integer,
                        Boolean, ForeignKey, create_engine, func)
from sqlalchemy.orm import relationship, backref, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.interfaces import PoolListener
import settings

Base = declarative_base()
conditions = ('AND', 'NOT', 'OR', 'COUNT', 'MAX', 'MIN', 'PAIRS', 'ODD')


class ForeignKeysListener(PoolListener):
    def connect(self, dbapi_con, con_record):
        db_cursor = dbapi_con.execute('pragma foreign_keys=ON')


engine = create_engine(
    f'sqlite:///{settings.DB_PATH}', listeners=[ForeignKeysListener()])


class Decimal(types.TypeDecorator):
    impl = types.String

    def __init__(self, precision=2, asdecimal=True, decimal_return_scale=2):
        self.precision = precision
        self.asdecimal = asdecimal = asdecimal
        self.decimal_return_scale = decimal_return_scale

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(types.VARCHAR(100))

    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        return D(value)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=func.now(), index=True)
    user_id = Column(Integer, default=-1)
    items = relationship(
        'OrderItem', cascade='all, delete-orphan', backref='order')

    def __init__(self, user_id: int=-1, ):
        self.user_id = user_id

    def __repr__(self):
        return (f'Order(id: {self.id}'
                f', created: {self.created}'
                f', items: {self.items}'
                ')')


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True, unique=True)
    price = Column(
        Decimal(precision=2, asdecimal=True, decimal_return_scale=2))
    rules = relationship(
        'ItemRules', cascade='all, delete-orphan', backref='item')

    def __init__(self, name, price=0, id=None):
        self.name = name
        self.price = price
        if id == 0:
            self.id = 0

    def __repr__(self):
        return (f'Item(id: {self.id}'
                f', name: «{self.name}»'
                f', price: {self.price}'
                # f', rules: {self.rules}'
                ')')


class Rule(Base):
    __tablename__ = 'rules'
    id = Column(Integer, primary_key=True)
    condition = Column(String, )  # 'OR[:[min_trigger:int], max_trigger:int]]'
    trigger_value = Column(Integer, default=0)
    discount = Column(
        Decimal(precision=2, asdecimal=True, decimal_return_scale=2))
    description = Column(String, index=True)
    item_rules = relationship(
        'ItemRules', cascade='all, delete-orphan', backref='rule')
    # item_rules

    def __init__(self, condition, trigger_value=1, discount=0, description=''):
        self.condition = condition
        self.trigger_value = trigger_value
        self.discount = discount
        self.description = description

    def __repr__(self):
        return (f'Rule(id: {self.id}, condition: {self.condition}, '
                f'trigger_value: {self.trigger_value}, '
                f'discount: {self.discount}, {self.description})')


class ItemRules(Base):
    __tablename__ = 'item_rules'
    """if item_id == 0 - неразборчивое правило"""
    item_id = Column(Integer, ForeignKey('items.id'),
                     index=True, primary_key=True, default=0)
    item_related_id = Column(Integer, index=True, primary_key=True)
    # 'OR[:[min_trigger:int], max_trigger:int]]'
    condition = Column(String, nullable=True)
    trigger_value = Column(Integer, default=0)
    result_value = Column(Integer, default=0)
    as_boolean = Column(Boolean, default=False)
    rule_id = Column(Integer, ForeignKey('rules.id'),
                     index=True, primary_key=True)

    def __init__(self, item, item_related_id, condition='AND', rule=None):
        self.item = item
        self.item_related_id = item_related_id
        self.condition = condition
        self.rule = rule

    def __repr__(self):
        return (f'ItemRules(item_id: {self.item_id}'
                f', item_related: {self.item_related_id}'
                f', condition: {self.condition}'
                f', rule.id: {self.rule.id}'
                f', rule.trigger_value: {self.rule.trigger_value}'
                ')')


class OrderItem(Base):
    __tablename__ = 'order_items'
    # id = Column(Integer, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), primary_key=True)
    # discount = DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = Column(Integer, default=1)
    item = relationship(Item, lazy='joined')

    def __init__(self, item, quantity=1):
        self.item = item
        self.quantity = quantity

    def __repr__(self):
        return (f'OrderItem(order.id: {self.order.id}'
                f', item: {self.item}'
                f', quantity: {self.quantity}'
                ')')


def get_items():
    session = Session(engine)
    items = session.query(Item).all()
    session.close()
    return items


def get_item(name):
    session = Session(engine)
    item = session.query(Item).filter_by(name=name)
    session.close()
    return item[0] if item else None


def get_order(order_id):
    session = Session(engine)
    order = session.query(Order).filter_by(id=order_id)
    session.close()
    return order[0] if order else None


def create_items(session):
    new_items = [Item(name=chr(r), price=10.91)
                 for r in range(ord('A'), ord('Z') + 1)]
    new_items.append(Item(id=0, name='Null Item'))
    session.add_all(new_items)
    session.commit()
    session.close()
    return new_items


if __name__ == '__main__':
    # print(settings.DB_PATH)
    # Base.metadata.drop_all(engine)
    items = {}
    Base.metadata.create_all(engine)
    session = Session(engine)
    session.add_all(create_items(session))
    items['A'] = session.query(Item).filter_by(name='A').one()
    items['B'] = session.query(Item).filter_by(name='B').one()
    ruleAB = Rule(condition='MIN', trigger_value=1,
                  description='Совместно A+B', discount=10)
    # session.add(rule)
    session.add_all([items['A'], items['B'], ruleAB])
    session.flush()
    # print(f'item_A: {item_A}')
    # print(f'item_B: {item_B}')
    item_rule = ItemRules(
        item=items['A'], item_related_id=items['B'].id,
        condition='AND', rule=ruleAB)
    session.add(item_rule)

    items['D'] = session.query(Item).filter_by(name='D').one()
    items['E'] = session.query(Item).filter_by(name='E').one()
    ruleDE = Rule(condition='MIN', trigger_value=1,
                  description='Совместоно D+E', discount=5)
    session.add_all([items['D'], items['E'], ruleDE])
    session.flush()
    item_rule = ItemRules(
        item=items['D'], item_related_id=items['E'].id,
        condition='AND', rule=ruleDE)
    session.add(item_rule)

    items['F'] = session.query(Item).filter_by(name='F').one()
    items['G'] = session.query(Item).filter_by(name='G').one()
    ruleEFG = Rule(condition='AND:MIN', trigger_value=1,
                   description='E+F+G', discount=5)
    session.add_all([items['E'], items['F'], items['G'], ruleEFG])
    session.flush()
    item_ruleEF = ItemRules(
        item=items['E'], item_related_id=items['F'].id,
        condition='AND', rule=ruleEFG)
    item_ruleEG = ItemRules(
        item=items['E'], item_related_id=items['G'].id,
        condition='AND', rule=ruleEFG)
    session.add_all([item_ruleEF, item_ruleEG])
    session.flush()

    items['K'] = session.query(Item).filter_by(name='K').one()
    items['L'] = session.query(Item).filter_by(name='L').one()
    items['M'] = session.query(Item).filter_by(name='M').one()
    ruleAKLM = Rule(condition='ONE:MIN', trigger_value=1,
                    description='A AND ONE(K, L, M)', discount=5)
    item_ruleAK = ItemRules(
        item=items['A'], item_related_id=items['K'].id,
        condition='AND', rule=ruleAKLM)
    item_ruleAL = ItemRules(
        item=items['A'], item_related_id=items['L'].id,
        condition='AND', rule=ruleAKLM)
    item_ruleAM = ItemRules(
        item=items['A'], item_related_id=items['M'].id,
        condition='AND', rule=ruleAKLM)
    session.add_all([ruleAKLM, item_ruleAK, item_ruleAL, item_ruleAM])
    session.flush()

    session.commit()
    items['0'] = session.query(Item).filter_by(id=0).one()
    items['C'] = session.query(Item).filter_by(name='C').one()
    promirule3 = Rule(
        condition='AND', description='3 w/o A, C', trigger_value=3, discount=5)
    promirules3_A = ItemRules(
        item=items['0'], item_related_id=items['A'].id, condition='NOT',
        rule=promirule3)
    promirules3_C = ItemRules(
        item=items['0'], item_related_id=items['C'].id, condition='NOT',
        rule=promirule3)
    session.add_all([promirule3, promirules3_A, promirules3_C])
    session.flush()
    promirule4 = Rule(
        condition='AND', description='4 w/o A, C', trigger_value=4, discount=10)
    promirules4_A = ItemRules(
        item=items['0'], item_related_id=items['A'].id, condition='NOT',
        rule=promirule4)
    promirules4_C = ItemRules(
        item=items['0'], item_related_id=items['C'].id, condition='NOT',
        rule=promirule4)
    session.add_all([promirule4, promirules4_A, promirules4_C])
    session.flush()
    promirule5 = Rule(
        condition='AND', description='4 w/o A, C', trigger_value=5, discount=20)
    promirules5_A = ItemRules(
        item=items['0'], item_related_id=items['A'].id, condition='NOT',
        rule=promirule5)
    promirules5_C = ItemRules(
        item=items['0'], item_related_id=items['C'].id, condition='NOT',
        rule=promirule5)
    session.add_all([promirule5, promirules5_A, promirules5_C])
    session.flush()
    # for item in session.query(Item).all():
    #     print(f'{item}')
    order = Order()
    order.items.append(OrderItem(items['A'], quantity=10))
    order.items.append(OrderItem(items['B'], quantity=10))
    session.add(order)
    session.commit()
    session.close()
