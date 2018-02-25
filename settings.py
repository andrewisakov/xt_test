#/usr/bin/python3
import logger as logger_
import os
import sys


APP_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(APP_DIR, 'xt_test.db')
#, pragmas=(('journal_mode', 'wal'), ('cache_size', -1024 * 64), ('foreign_keys', 'ON')))

logger = logger_.rotating_log(os.path.join(APP_DIR, 'xt.log'), 'xt')
