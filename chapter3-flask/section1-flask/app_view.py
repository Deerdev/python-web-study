# coding=utf-8
from flask import Flask, request, render_template
from flask.views import View
# 即插视图的灵感来自Django的基于类而不是函数的通用视图方式，这样的视图就可以支持继承了
# 标准视图
# 模板存放在~/web_develop/templates下，使用__name__来获取模板目录，template_folder是相对于app.py文件的，需要设置成'../../templates'才能找到正确的模板目录。
app = Flask(__name__, template_folder='../../templates')


# 标准视图需要继承flask.views.View，必须实现dispatch_request
class BaseView(View):
    def get_template_name(self):
        raise NotImplementedError()

    def render_template(self, context):
        return render_template(self.get_template_name(), **context)

    def dispatch_request(self):
        if request.method != 'GET':
            return 'UNSUPPORTED!'
        context = {'users': self.get_users()}
        return self.render_template(context)


class UserView(BaseView):

    def get_template_name(self):
        return 'chapter3/section1/users.html'

    def get_users(self):
        return [{
            'username': 'fake',
            'avatar': 'http://lorempixel.com/100/100/nature/'
        }]


app.add_url_rule('/users', view_func=UserView.as_view('userview'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)
