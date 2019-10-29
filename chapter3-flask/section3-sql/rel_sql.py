# coding=utf-8
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from consts import DB_URI

eng = create_engine(DB_URI)
Base = declarative_base()

# InnoDB类型的表可以使用外键进行多表关联，保证数据的一致性和实现一些级联操作


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email_address = Column(String(128), nullable=False)
    # Address表的user_id字段其实就是User的id字段，使用ForeignKey关联之后，就不需要在Address上独立存储一份user_id数据
    user_id = Column(Integer, ForeignKey('users.id'))
    # user字段关联到User表
    user = relationship('User', back_populates='addresses')


# 这个字段需要放在Address类定义之后
User.addresses = relationship('Address', order_by=Address.id,
                              back_populates='user')


Base.metadata.drop_all(bind=eng)
Base.metadata.create_all(bind=eng)

Session = sessionmaker(bind=eng)
session = Session()

user = User(name='xiaoming')

user.addresses = [Address(email_address='a@gmail.com', user_id=user.id),
                  Address(email_address='b@gmail.com', user_id=user.id)]
session.add(user)
session.commit()

# > 虽然使用外键可以降低开发成本，减少数据量，但是在用户量大、并发度高的时候，不推荐使用外键来关联，数据的一致性和完整性问题可以通过事务来保证。
