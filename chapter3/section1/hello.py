# coding=utf-8
from flask import Flask

# 让flask.helpers.get_root_path函数通过传入这个名字确定程序的根目录
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
