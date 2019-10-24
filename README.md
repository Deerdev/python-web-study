# Python Web开发实战

《Python Web开发实战》学习笔记

> Python2.7

# 配置

安装 virtualenv-burrito：

```py
＞ curl -sL https://raw.githubusercontent.com/brainsik/virtualenv-burrito/master/virtualenv-burrito.sh | $SHELL
```

它自动把初始化脚本放在`/home/ubuntu/.zprofile`里面，这样在下次登录之后就可以使用了。如果想立刻使用初始化脚本，可以用如下语句：

```py
source /home/ubuntu/.venvburrito/startup.sh`
```

startup.sh会自动创建了`~/.virtualenvs`作为WORKON_HOME，用法和virtualenvwrapper是一样的。

To create a new virtualenv:

```
mkvirtualenv newname
```

Once activated, `pip install <package>` (without using sudo) whichever Python packages you want. They'll only be available in that virtualenv. You can make as many virtualenvs as you want.

To switch between virtualenvs:
```
workon othername
```

启动虚拟环境后 pip 无法使用：
```
Traceback (most recent call last):
  File "/Users/walt.lu/.virtualenvs/python-web-study/bin/pip", line 6, in <module>
    from pip._internal.main import main
ImportError: No module named main
```

重新安装
```py
# 重新安装
easy_install pip
```

使用如下命令即可对virtualenv和virtualenvwrapper进行更新：

```py
＞ virtualenv-burrito upgrade 
```

# Flask

安装 Flask：
```py
pip install Flask
```