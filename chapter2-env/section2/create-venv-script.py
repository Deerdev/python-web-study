# coding=utf-8
import subprocess

import virtualenv

# 首先修改virtualenv配置文件的权限为可写入 sudo chown ubuntu:ubuntu`which virtualenv`
# 给virtualenv添加默认行为（安装flake8）
virtualenv_path = subprocess.check_output(['which', 'virtualenv']).strip()

EXTRA_TEXT = '''
def after_install(options, home_dir):
    subprocess.call(['{}/bin/pip'.format(home_dir), 'install', 'flake8'])
'''


def main():
    text = virtualenv.create_bootstrap_script(EXTRA_TEXT, python_version='2.7')
    print 'Updating %s' % virtualenv_path

    # 把配置写回到virtualenv_path的默认配置文件中
    with open(virtualenv_path, 'w') as f:
        f.write(text)


if __name__ == '__main__':
    main()
