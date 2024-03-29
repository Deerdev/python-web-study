# coding=utf-8
from flask_script import Manager, Server, Shell, prompt_bool
# 使用 flask_script(pip install flask-script)
from app import app, db, PasteFile

manager = Manager(app)

# 模仿 django 的 manage.py


def make_shell_context():
    return {
        'db': db,
        'PasteFile': PasteFile,
        'app': app
    }

# python manage.py dropdb #在测试环境里可以用来清理数据
@manager.command
def dropdb():
    if prompt_bool(
            'Are you sure you want to lose all your data'):
        db.drop_all()

# python manage.py get_file -h ec12e434b48648f0a65ac28a28759ba5.jpg #在终端通过filehash获取文件路径
@manager.option('-h', '--filehash', dest='filehash')
def get_file(filehash):
    paste_file = PasteFile.query.filter_by(filehash=filehash).first()
    if not paste_file:
        print 'Not exists'
    else:
        print 'URL is {}'.format(paste_file.get_url('i'))


# python manage.py shell #自带了三个内置变量的shell
manager.add_command('shell', Shell(make_context=make_shell_context))
# python manage.py runserver #通过manage.py启动服务
manager.add_command('runserver', Server(
    use_debugger=True, use_reloader=True,
    host='0.0.0.0', port=9000)
)


if __name__ == '__main__':
    manager.run()
