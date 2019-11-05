# coding=utf-8
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
# 使用 flask_debugtoolbar (pip install flask-debugtoolbar)
# 在浏览器上添加右边栏，可以快速查看环境变量、上下文内容，方便调试 （测试前端页面）
app = Flask(__name__)

app.debug = True

app.config['SECRET_KEY'] = 'a secret key'

toolbar = DebugToolbarExtension(app)


@app.route('/')
def hello():
    return '<body></body>'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=app.debug)
