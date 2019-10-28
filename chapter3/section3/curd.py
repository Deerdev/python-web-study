# coding=utf-8
import MySQLdb
from consts import HOSTNAME, DATABASE, USERNAME, PASSWORD


con = MySQLdb.connect(HOSTNAME, USERNAME, PASSWORD, DATABASE)

# 使用了with语句。connect的__enter__方法返回了游标，在with中执行结束，它会判断当前是否有错误，有错误就回滚，没有则进行事务提交
with con as cur:
    cur.execute('drop table if exists users')
    cur.execute('create table users(Id INT PRIMARY KEY AUTO_INCREMENT, '
                'Name VARCHAR(25))')
    cur.execute("insert into users(Name) values('xiaoming')")
    cur.execute("insert into users(Name) values('wanglang')")
    cur.execute('select * from users')

    rows = cur.fetchall()
    for row in rows:
        print row
    cur.execute('update users set Name=%s where Id=%s', ('ming', 1))
    print 'Number of rows updated:',  cur.rowcount

    cur = con.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from users')

    rows = cur.fetchall()
    for row in rows:
        print row['Id'], row['Name']
