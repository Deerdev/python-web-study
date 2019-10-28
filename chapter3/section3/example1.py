# coding=utf-8
import MySQLdb
from consts import HOSTNAME, DATABASE, USERNAME, PASSWORD

try:
    con = MySQLdb.connect(HOSTNAME, USERNAME, PASSWORD, DATABASE)
    # con.cursor()返回一个游标，数据库操作都是在游标实例上执行的
    cur = con.cursor()
    # cur.execute方法传入的就是要执行的SQL语句。
    cur.execute("SELECT VERSION()")
    # cur.fetchone()返回执行结果，这一点一开始可能不适应，因为数据库操作的结果不是在execute中直接返回的，而需要使用fetchone、fetchall、fetchmany这样的方法获取结果
    ver = cur.fetchone()
    print "Database version : %s " % ver
except MySQLdb.Error as e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    exit(1)
finally:
    # 关闭数据库
    if con:
        con.close()
