# coding=utf-8
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request, jsonify
from flask_sqlalchemy import get_debug_queries

from ext import db
from users import User

# mysql 慢查询
# 借用SQLALCHEMY_RECORD_QUERIES和DATABASE_QUERY_TIMEOUT将慢查询及相关上下文信息记录到日志中
app = Flask(__name__)
app.config.from_object('config')
# 值为0.0001只是为了演示，生产环境需要按需调大这个阈值。
app.config['DATABASE_QUERY_TIMEOUT'] = 0.0001
app.config['SQLALCHEMY_RECORD_QUERIES'] = True
db.init_app(app)

formatter = logging.Formatter(
    "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
handler = RotatingFileHandler('slow_query.log', maxBytes=10000, backupCount=10)
handler.setLevel(logging.WARN)
handler.setFormatter(formatter)
# 给app.logger添加一个记录日志到名为slow_query.log的文件的处理器，这个日志会按大小切分。
app.logger.addHandler(handler)

with app.app_context():
    db.drop_all()
    db.create_all()


@app.route('/users', methods=['POST'])
def users():
    username = request.form.get('name')

    user = User(username)
    print 'User ID: {}'.format(user.id)
    db.session.add(user)
    db.session.commit()

    return jsonify({'id': user.id})

# 添加after_request钩子，每次请求结束后获取执行的查询语句，假如超过阈值则记录日志。
@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= app.config['DATABASE_QUERY_TIMEOUT']:
            app.logger.warn(
                ('\nContext:{}\nSLOW QUERY: {}\nParameters: {}\n'
                 'Duration: {}\n').format(query.context, query.statement,
                                          query.parameters, query.duration))
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
