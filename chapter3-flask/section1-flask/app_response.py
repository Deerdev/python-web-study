# coding=utf-8
from flask import Flask, jsonify
from werkzeug.wrappers import Response
app = Flask(__name__)

# 自定义json序列化
class JSONResponse(Response):
    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, dict):
            rv = jsonify(rv)
        return super(JSONResponse, cls).force_type(rv, environ)

app.response_class = JSONResponse


@app.route('/')
def hello_world():
    return {'message': 'Hello World!'}


@app.route('/custom_headers')
def headers():
    # 返回json格式 header
    return {'headers': [1, 2, 3]}, 201, [('X-Request-Id', '100')]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
