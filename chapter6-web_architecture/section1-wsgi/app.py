# coding=utf-8
from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
# gunicorn使用
# gunicorn --workers=3 chapter6.section1.app:app -b 0.0.0.0:9000
# chapter6.section1是模块目录的名字，第一个app是模块文件名字，第二个app是文件中Flask实例的名字。
# Worker的数量并不是越多越好，推荐值是CPU的个数× 2+1，CPU个数使用如下的方式获取：
# > python -c 'import multiprocessing; print multiprocessing.cpu_count()'
