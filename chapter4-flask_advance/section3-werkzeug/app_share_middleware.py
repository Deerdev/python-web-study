# coding=utf-8
import os

from flask import Flask
from werkzeug.wsgi import SharedDataMiddleware
# 静态文件都应该使用Nginx来服务，但是在测试环境中或者对资源响应要求不高时，也可以使用SharedDataMiddleware来提供这样的服务，之前实现的文件托管服务也使用了它
app = Flask(__name__)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/static/': os.path.join(os.path.dirname(__file__), 'static')
})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
