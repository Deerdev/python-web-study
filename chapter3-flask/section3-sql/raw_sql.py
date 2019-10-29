# coding=utf-8
from sqlalchemy import create_engine
from consts import DB_URI

# 使用 sqlalchemy 原生写 sql
eng = create_engine(DB_URI)
with eng.connect() as con:
    con.execute('drop table if exists users')
    con.execute('create table users(Id INT PRIMARY KEY AUTO_INCREMENT, '
                'Name VARCHAR(25))')
    con.execute("insert into users(name) values('xiaoming')")
    con.execute("insert into users(name) values('wanglang')")
    # 直接通过返回值获取结果
    rs = con.execute('select * from users')
    for row in rs:
        print row
