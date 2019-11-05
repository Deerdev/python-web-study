# coding=utf-8
import os.path

from flask import Flask, redirect, url_for
from flask_admin import Admin
from flask_login import (current_user, UserMixin, LoginManager,
                         login_user, logout_user)
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.base import MenuLink, BaseView, expose


from ext import db
from users import User as _User

# 有了Flask-Admin的帮助，我们用很少的代码就能像Django那样实现一个管理后台。它支持Pymongo、Peewee、Mongoengine、SQLAlchemy等数据库使用方法，自带了基于模型的数据管理、文件管理、Redis的页面命令行等类型后台。尤其是模型的管理后台,甚至可以细粒度定制字段级别的权限。

# ＞ pip install Flask-Admin


# 现在基于Flask-Login和Flask-SQLAlchemy实现包含如下功能的后台（app_admin.py）：
# - 可以在后台操作数据库中的数据。
# - 静态文件管理。
# - 在导航栏添加一些链接和视图，比如笔者的GitHub地址、Google链接以及回首页的链接。还添加一个动态的链接，点击它可以登录和退出。当登录后会动态地添加一个“Authenticated”的链接。
# - 自定义点击“Authenticated”的链接后看到的模板。

app = Flask(__name__, template_folder='../../templates',
            static_folder='../../static')
app.config.from_object('config')
USERNAME = 'xiaoming'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


# 第一步还是定义User模型，本例借用users.py里面的User，再继承UserMixin即可
class User(_User, UserMixin):
    pass


@app.before_first_request
def create_user():
    db.drop_all()
    db.create_all()

    user = User(name=USERNAME, email='a@dongwm.com', password='123')
    db.session.add(user)
    db.session.commit()


class AuthenticatedMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated


class NotAuthenticatedMenuLink(MenuLink):
    def is_accessible(self):
        return not current_user.is_authenticated


@login_manager.user_loader
def user_loader(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user


class MyAdminView(BaseView):
    @expose('/')
    def index(self):
        return self.render('chapter4/section2/authenticated-admin.html')

    def is_accessible(self):
        return current_user.is_authenticated

# 添加主页、登录和退出的视图
@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


@app.route('/login/')
def login_view():
    user = User.query.filter_by(name=USERNAME).first()
    login_user(user)
    return redirect(url_for('admin.index'))


@app.route('/logout/')
def logout_view():
    logout_user()
    return redirect(url_for('admin.index'))


admin = Admin(app, name='web_develop', template_mode='bootstrap3')
# 在Flask-Admin中指定视图需要继承它提供的BaseView，或者使用contrib中自带的视图类，比如FileAdmin和ModelView：
admin.add_view(ModelView(User, db.session))

path = os.path.join(os.path.dirname(__file__), '../../static')
admin.add_view(FileAdmin(path, '/static/', name='Static Files'))

# 创建一个名为Authenticated的链接，但是必须登录才能访问
admin.add_view(MyAdminView(name='Authenticated'))

admin.add_link(MenuLink(name='Back Home', url='/'))
admin.add_link(NotAuthenticatedMenuLink(name='Login',
                                        endpoint='login_view'))

# 其中category会创建一个叫作Links的下拉菜单，把Google和GitHub链接放进去
admin.add_link(MenuLink(name='Google', category='Links',
                        url='http://www.google.com/'))
admin.add_link(MenuLink(name='Github', category='Links',
                        url='https://github.com/dongweiming'))
admin.add_link(AuthenticatedMenuLink(name='Logout',
                                     endpoint='logout_view'))

# MyAdminView定义的首页地址没有验证是不能访问的。
# 上面提到的视图可以通过设置endpoint参数自定义链接，比如“ModelView(User, db.session)”生成的子路径是“/admin/user”，修改为：“ModelView(User, db.session, endpoint='new_user')”，就可以使用“/admin/new_user”来访问了。
# 提到的authenticated-admin.html模板就是我们自定义的点击Authenticated的链接后看到的模板。它的内容如下：
# {%extends 'admin/master.html'%}
# {%block body%}
#     Hello World from Authenticated Admin!
# {%endblock%}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)
