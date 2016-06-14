
import os
from os.path import dirname
import sys
import MySQLdb

root_path = dirname(dirname(os.getcwd()))
require_path = os.path.join(root_path, 'lib\\simplequery')
sys.path.append(require_path)

from table_data import *
from simplequery import *


def get_mysql_connection():
    args = {'host':'localhost', 'user':'root', 'passwd':'root', 'db':"test"}
    conn = MySQLdb.connect(**args)

    with conn.cursor() as c:
        c.execute('show databases;')
        
        print(list(map(lambda x: x[0], c.fetchall())))
    return conn

def usage():
    print('Help:')

"""
Run file with argv[]
"""
if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        exit()

    e = SimpleQueryExecutor()
    conn = get_mysql_connection()
    #print(conn)
    #exit()
    e.set_connection(conn)
    filename = sys.argv[1]
    params = None
    if len(sys.argv) > 2:
        params = sys.argv[2:]
    if os.path.exists(filename):
        e.run_file(filename, params)


