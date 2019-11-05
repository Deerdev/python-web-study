# coding=utf-8
from collections import OrderedDict

from flask import Flask, jsonify
from werkzeug.wrappers import Response
from werkzeug.wsgi import DispatcherMiddleware

app = Flask(__name__)
json_page = Flask(__name__)
# DispatcherMiddleware是可以调度多个应用的中间件


class JSONResponse(Response):
    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, dict):
            rv = jsonify(rv)
        return super(JSONResponse, cls).force_type(rv, environ)


json_page.response_class = JSONResponse


@json_page.route('/hello/')
def hello():
    return {'message': 'Hello World!'}


@app.route('/')
def index():
    return 'The index page'


# 当访问以/json开头的地址时都默认自动用jsonify格式化, 访问其他地址不受影响
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, OrderedDict((
    ('/json', json_page),
)))

# 使用这个中间件对访问地址是有副作用的，“@json_page.route('/')”等价于“@app.route('/json/')”，也就是子路径的地址前面是有/json前缀的，这一点比较隐晦。
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
