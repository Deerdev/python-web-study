# coding=utf-8
from flask import Flask, request, jsonify

from ext import db
from users import User

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)

# drop_all和create_all要在定义model之后再执行。Flask-SQLAlchemy要求执行的时候有应用上下文，但是在这里还没有，所以需要使用“with app.app_context()”创建应用上下文。关于应用上下文稍后会详细介绍，也会介绍正确的用法
with app.app_context():
    db.drop_all()
    db.create_all()


@app.route('/users', methods=['POST'])
def users():
    username = request.form.get('name')

    user = User(username)
    # print的user.id永远是None，因为在没有commit之前还没有创建它。commit之后user.id会自动改成在表中创建的条目id。
    print 'User ID: {}'.format(user.id)
    db.session.add(user)
    db.session.commit()

    return jsonify({'id': user.id})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
