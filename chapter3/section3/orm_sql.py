# coding=utf-8
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_, or_
from sqlalchemy.orm import sessionmaker

from consts import DB_URI

eng = create_engine(DB_URI)
Base = declarative_base()

# ORM是基于SQLAlchemy表达式语言的


class User(Base):
    # 定义的User类会生成一张表，__tablename__的值就是表名
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'),
                primary_key=True, autoincrement=True)
    name = Column(String(50))


Base.metadata.drop_all(bind=eng)
Base.metadata.create_all(bind=eng)

# 通过sessionmaker创建一个会话，会话提供了事务控制的支持。模型实例对象本身独立存在，如果要让其修改（创建）生效，需要把它们加入某个会话；如果不希望对其生效就从会话中去掉由session管理的实例对象。执行session.commit()时修改被提交到数据库，执行session.rollback()可以回滚变更。
Session = sessionmaker(bind=eng)
session = Session()

session.add_all([User(name=username)
                 for username in ('xiaoming', 'wanglang', 'lilei')])

session.commit()


def get_result(rs):
    print '-' * 20
    for user in rs:
        print user.name


rs = session.query(User).all()
get_result(rs)
rs = session.query(User).filter(User.id.in_([2, ]))
get_result(rs)
rs = session.query(User).filter(and_(User.id > 2, User.id < 4))
get_result(rs)
rs = session.query(User).filter(or_(User.id == 2, User.id == 4))
get_result(rs)
rs = session.query(User).filter(User.name.like('%min%'))
get_result(rs)
user = session.query(User).filter_by(name='xiaoming').first()
get_result([user])
