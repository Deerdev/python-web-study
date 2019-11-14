# coding=utf-8
import ast
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import msgpack

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://web:web@localhost:3306/r'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# 直接通过redis存储数据Obj，但是需要序列化和反序列化（使用 msgpack-python)


class PasteFile(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(5000), nullable=False)
    uploadtime = db.Column(db.DateTime, nullable=False)

    def __init__(self, name='', uploadtime=None):
        self.uploadtime = datetime.now() if uploadtime is None else uploadtime
        self.name = name

    def to_dict(self):
        # 不一定整个对象的全部方法都要缓存，缓存对象中有用的属性就可以了
        d = {k: v for k, v in vars(self).items() if not k.startswith('_')}
        # # datetime格式不能被序列化，需要先转换成对应的时间字符串
        d['uploadtime'] = d['uploadtime'].strftime('%Y%m%dT%H:%M:%S.%f')
        return str(d)  # 序列化的数据必须是字符串类型

    @classmethod
    def from_dict(cls, data):
        data = ast.literal_eval(data)
        # id是自增长的字段，没有在__init__中传入，需要在生成对象之后再赋值id这个属性
        id = data.pop('id')
        data['uploadtime'] = datetime.strptime(
            data['uploadtime'], '%Y%m%dT%H:%M:%S.%f')
        p = cls(**data)
        p.id = id
        return p


def default(obj):
    if isinstance(obj, PasteFile):
        return msgpack.ExtType(42, obj.to_dict())
    raise TypeError('Unknown type: %r' % (obj,))


def ext_hook(code, data):
    if code == 42:
        p = PasteFile.from_dict(data)
        return p
    return msgpack.ExtType(code, data)


p = PasteFile.query.get(100)
# print p

packed = msgpack.packb(p, default=default)  # 序列化
# print packed

unpacked = msgpack.unpackb(packed, ext_hook=ext_hook)  # 反序列化
# print unpacked

# print unpacked.id, unpacked.name, unpacked.uploadtime
