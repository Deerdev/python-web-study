# coding=utf-

# ext模块存放了Flask第三方的扩展：
# from flask_sqlalchemy import SQLAlchemy
# db=SQLAlchemy()

# 这样的好处是，db是一个没有依赖的常量，app也可以“from ext import db”，不会造成循环依赖。
from ext import db

# 在Flask中使用SQLAlchemy
# db.Model其实还是基于declarative_base实现的，Flask-SQLAlchemy提供了一个和Django风格很像的基类。在这里重新定义了User的__init__方法，因为它默认需要传入所有字段，而id是一个自增长的字段，不需要传入


class User(db.Model):
    __tablename__ = 'users2'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name
