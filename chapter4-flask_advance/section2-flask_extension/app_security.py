# coding=utf-8
from functools import wraps, reduce
from operator import or_

from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user
from flask_security import (Security, SQLAlchemyUserDatastore,
                            UserMixin, RoleMixin, login_required)
from flask_security.forms import LoginForm

# Flask-Security非常强大，它提供角色管理、权限管理、用户登录、邮箱验证、密码重置、密码加密、跟踪用户登录状态等功能。先安装它：
#     ＞ pip install flask-security
# Flask-Security提供了7种基本模板。如果想要定制模板，可以在应用的模板目录下创建名为security的目录，添加对应名字的模板

# Flask-Security还提供了8种上下文处理的装饰器，类似于钩子

app = Flask(__name__, template_folder='../../templates')
app.config.from_object('config')
# 指定新的模板
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'chapter4/section2/login_user.html'  # noqa
app.config['SECURITY_PASSWORD_SALT'] = 'salt'


db = SQLAlchemy(app)

# 使用位运算做权限控制。位运算在Linux文件系统上就有体现，一个用户对文件或目录所拥有的权限分为三种：“可读（1）”、“可写（2）”和“可执行（4）”，它们之间可以任意组合：有可读和可写权限就用3来表示（1+2=3）；有可读和可执行权限就用5来表示（1+4=5），三种权限全部拥有就用7表示（1+2+4=7）

# 就把它们中都为1的标志位置为1，如果结果还等于B，就说明它有这样的权限
# In:int('00000111', 2)&int('00000001', 2)==int('00000001', 2)
# Out:True

# In:int('00000100', 2)&int('00000001', 2)==int('00000001', 2)
# Out:False


class Permission(object):
    LOGIN = 0x01
    EDITOR = 0x02
    OPERATOR = 0x04
    ADMINISTER = 0xff   # 拥有全部权限
    PERMISSION_MAP = {
        LOGIN: ('login', 'Login user'),
        EDITOR: ('editor', 'Editor'),
        OPERATOR: ('op', 'Operator'),
        ADMINISTER: ('admin', 'Super administrator')
    }


# 用户和角色是多对多的关系，需要定义一个用于关系的辅助表。对于这个辅助表，强烈建议不使用模型，而是采用一个实际的表
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer,
              db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    permissions = db.Column(db.Integer, default=Permission.LOGIN)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    # 给User这个模型添加roles字段，指向模型Role，并且添加判断权限的方法
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    # 上面的db.relationship还使用了backref，它表示反向引用,Role对象通过users就能反向获取有对应权限的用户列表

    def can(self, permissions):
        if self.roles is None:
            return False
        all_perms = reduce(or_, map(lambda x: x.permissions, self.roles))
        return all_perms & permissions == permissions

    def can_admin(self):
        return self.can(Permission.ADMINISTER)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, register_form=LoginForm)

# 添加login_context_processor钩子,登录时视图会触发
@security.login_context_processor
def security_login_processor():
    print 'Login'
    return {}


# 验证访问权限的装饰器
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def _deco(*args, **kwargs):
            # current_user就是一个User对象，通过User类添加的can方法判断权限
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return _deco
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)

# 通过添加before_first_request钩子实现初始化
@app.before_first_request
def create_user():
    db.drop_all()
    db.create_all()

    # 每次在第一次接收请求的时候就会删除相关表，再重新创建这些表，并创建两个用户，用户权限分别如下。
    # dongwm@dongwm.com：它具有LOGIN与EDITOR两种权限，但有些页面访问不了。
    # admin@dongwm.com：管理员，拥有全部的权限。
    for permissions, (name, desc) in Permission.PERMISSION_MAP.items():
        user_datastore.find_or_create_role(
            name=name, description=desc, permissions=permissions)
    for email, passwd, permissions in (
            ('dongwm@dongwm.com', '123', (
                Permission.LOGIN, Permission.EDITOR)),
            ('admin@dongwm.com', 'admin', (Permission.ADMINISTER,))):
        user_datastore.create_user(email=email, password=passwd)
        for permission in permissions:
            user_datastore.add_role_to_user(
                email, Permission.PERMISSION_MAP[permission][0])
    db.session.commit()


@app.route('/')
@login_required
@permission_required(Permission.LOGIN)
def index():
    return 'Login in'


@app.route('/admin/')
@login_required
@admin_required
def admin():
    return 'Only administrators can see this!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=app.debug)
