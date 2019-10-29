import subprocess

import virtualenv

# Virtualenv定制脚本接受3个扩展函数。
# extend_parser(optparse_parser)：添加额外的选项。
# adjust_options(options, args)：改变当前的选项。
# after_install ： 在默认的环境安装好之后 ， 执行其他工作 ， 主要通过这个函数完成定制 。 现在做一个更复杂的定制 ， 实现如下需求 ：

virtualenv_path = subprocess.check_output(['which', 'virtualenv']).strip()

# 此处添加 -r 参数，安装对应的依赖包
EXTRA_TEXT = '''
ROOT_PATH = '/home/ubuntu/venv'


def extend_parser(parser):
    parser.add_option(
        '-r','--req', action='append', type='string', dest='reqs',
        help="specify additional required packages", default=[])


def adjust_options(options, args):
    if not args:
        return

    base_dir = args[0]
    args[0] = join(ROOT_PATH, base_dir)


def after_install(options, home_dir):
    if not options.reqs:
        logger.warn('Warn: You maybe need specify some required packages!')

    for req in options.reqs:
        subprocess.call(['{}/bin/pip'.format(home_dir), 'install', req])
'''


def main():
    text = virtualenv.create_bootstrap_script(EXTRA_TEXT, python_version='2.7')
    print 'Updating %s' % virtualenv_path
    with open(virtualenv_path, 'w') as f:
        f.write(text)

if __name__ == '__main__':
    main()


# 现在创建一个自动安装Flake8和Jinja2的虚拟环境(通过新增的 -r 参数实现)：
# ＞ virtualenv tmp2 -r flake8 -r jinja2