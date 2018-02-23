#/usr/bin/python3
from peewee import SqliteDatabase
import logging
import os
import sys


APP_PATH = os.path.dirname(__file__)
db = SqliteDatabase(os.path.join(APP_PATH, 'xt_test.db'))
