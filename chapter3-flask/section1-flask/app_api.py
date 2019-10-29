# coding=utf-8
from flask import Flask, jsonify
from flask.views import MethodView

app = Flask(__name__)

# 基于调度方法的视图
# lask.views.MethodView对每个HTTP方法执行不同的函数（映射到对应方法的小写的同名方法上），这对RESTful API尤其有用


class UserAPI(MethodView):

    def get(self):
        return jsonify({
            'username': 'fake',
            'avatar': 'http://lorempixel.com/100/100/nature/'
        })

    def post(self):
        return 'UNSUPPORTED!'


app.add_url_rule('/user', view_func=UserAPI.as_view('userview'))

# 通过装饰as_view的返回值来实现对于视图的装饰功能，常用于权限的检查、登录验证等：
#     def user_required(f):
#         def decorator(*args,**kwargs):
#             if not g.user:
#                 abort(401)
#             return f(*args,**kwargs)
#         return decorator

#     view=user_required(UserAPI.as_view('users'))
#     app.add_url_rule('/users/', view_func=view)
# 从Flask 0.8开始，还可以通过在继承MethodView的类中添加decorators属性来实现对视图的装饰：
#     class UserAPI(MethodView):
#         decorators = [user_required]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
