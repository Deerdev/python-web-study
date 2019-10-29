# coding=utf-8
import random

from flask import Flask, g, render_template
from ext import db
from users import User
app = Flask(__name__, template_folder='../../templates')
app.config.from_object('config')
db.init_app(app)

# 上下文


def get_current_user():
    users = User.query.all()
    return random.choice(users)

# 6个钩子函数
# 在处理第一次请求之前执行
# setup函数常用来初始化数据，尤其是开发环境下，每次启动应用都会先删掉之前创建的假数据再重新创建。
@app.before_first_request
def setup():
    db.drop_all()
    db.create_all()
    fake_users = [
        User('xiaoming', 'xiaoming@dongwm.com'),
        User('dongwweiming', 'dongwm@dongwm.com'),
        User('admin', 'admin@dongwm.com')
    ]
    db.session.add_all(fake_users)
    db.session.commit()

# 在每次请求前执行
# 之前说flask.g是一个应用上下文，通常放在before_request中对它进行数据的填充
@app.before_request
def before_request():
    g.user = get_current_user()

# 不管是否有异常，注册的函数都会在每次请求之后执行
# 一般来说，对资源的操作有一个get_X和一个teardown_X对应，多个资源的使用可以使用同一个teardown函数。teardown通常是做一些环境的清理工作，提交未提交的操作请求等，在本地开发环境和测试时意义较大。
@app.teardown_appcontext
def teardown(exc=None):
    if exc is None:
        db.session.commit()
    else:
        db.session.rollback()
    db.session.remove()
    g.user = None

# 上下文处理的装饰器，返回的字典中的键可以在上下文中使用（加入到是上下文中）
# 由于Jinja2模板的限制，并不能直接使用enumerate这样的Python自带的函数（虽然Jinja2支持在for循环中使用loop.index和loop.index0，但是无法满足全部需要），可以使用context_processor把要用到的上下文资源传进去。这样在模板中就可以直接使用enumerate和current_user了。
@app.context_processor
def template_extras():
    return {'enumerate': enumerate, 'current_user': g.user}

# errorhandler接收状态码，可以自定义返回这种状态码的响应的处理方法。
# errorhandler除了可自定义对不同错误状态码的返回内容，还可以传入自定义的异常对象。
@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404

# 在使用Jinja2模板的时候可以方便地注册过滤器
# 虽然Jinja2支持了非常多的过滤器，但还是无法满足我们的全部需要。注册一个新的过滤器很方便，这个例子中注册了一个叫作capitalize的过滤器，在模板中可以这样使用“{{user.name|capitalize}}”。
@app.template_filter('capitalize')
def reverse_filter(s):
    return s.capitalize()


@app.route('/users')
def user_view():
    users = User.query.all()
    return render_template('chapter3/section4/user.html', users=users)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
