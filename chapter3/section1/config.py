# coding=utf-8
DEBUG = False

# 可选导入本地local_settings配置，没有就不导入
try:
    from local_settings import *
except ImportError:
    pass
