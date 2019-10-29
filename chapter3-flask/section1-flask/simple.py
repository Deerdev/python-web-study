# coding=utf-8

# 跳转和重定向
from flask import Flask, request, abort, redirect, url_for

app = Flask(__name__)
app.config.from_object('config')

# 访问/people的请求会被301跳转到/people/上，保证了URL的唯一性
@app.route('/people/')
def people():
    name = request.args.get('name')
    if not name:
        return redirect(url_for('login'))
    # request.headers存放了请求的头信息，通过它可以获取UA值
    user_agent = request.headers.get('User-Agent')
    return 'Name: {0}; UA: {1}'.format(name, user_agent)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.headers.get('user_id')
        return 'User: {} login'.format(user_id)
    else:
        return 'Open Login page'


@app.route('/secret/')
def secret():
    # 执行abort(401)会放弃请求并返回错误代码401，表示禁止访问。之后的语句永远不会被执行
    abort(401)
    print 'This is never executed'


if __name__ == '__main__':
    # 能使用debug=app.debug是因为flask.config.ConfigAttribute在app中做了配置的代理，目前存在的配置代理项有:
    # app.debug->DEBUG
    # app.testing->TESTING
    # app.secret_key->SECRET_KEY
    # app.session_cookie_name->SESSION_COOKIE_NAME
    # app.permanent_session_lifetime->PERMANENT_SESSION_LIFETIME
    # app.use_x_sendfile->USE_X_SENDFILE
    # app.logger_name->LOGGER_NAME

    # 此处app.debug其实就是app.config['DEBUG']。
    # config.py 里配置为 False
    app.run(host='0.0.0.0', port=9000, debug=app.debug)
