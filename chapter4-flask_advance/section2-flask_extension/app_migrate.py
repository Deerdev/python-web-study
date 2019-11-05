# coding=utf-8
from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
# 使用 flask_migrate（pip install Flask-Migrate）
# 修改数据库模型和更新数据库
from ext import db

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)

import users  # noqa

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()


# 1.初始化迁移工作： python ./app_migrate.py db init
#    会在当前目录下增加一个migrations目录，这个目录应该放进版本库
# 2. 修改数据库字段后：python ./app_migrate.py db migrate
#    会在migrations/versions/目录下添加一个执行的脚本，文件名就是版本号。版本的对应关系在当前库的alembic_version表中。需要注意的是，假如你的数据库里还有其他的表没有放到迁移脚本中，就会被删掉，所以app_migrate.py这样的管理脚本应该覆盖所有重要的表，而所有模型文件都使用“from ext import db”，就可以保证这一点。
#    这一步并没有实际操作数据库，所以一定要注意终端输出，确定和自己的预想一样
# 3. 更新到数据库：python ./app_migrate.py db upgrade
