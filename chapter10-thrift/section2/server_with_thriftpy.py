# coding=utf-8
import os
import logging

import thriftpy
from thriftpy.rpc import make_server
from thriftpy.protocol import TBinaryProtocolFactory
from thriftpy.transport import TBufferedTransportFactory

# 使用 thriftpy（https://github.com/eleme/thriftpy）的例子

HERE = os.path.abspath(os.path.dirname(__file__))
logging.basicConfig()   # 这一步很重要，可以收到Thrift发出来的异常日志

calc_thrift = thriftpy.load(
    os.path.join(HERE, 'calc.thrift'),
    module_name='calc_thrift')


class Dispatcher(object):
    def add(self, a, b):
        return a + b


server = make_server(calc_thrift.CalcService,
                     Dispatcher(),
                     '127.0.0.1', 8300,
                     proto_factory=TBinaryProtocolFactory(),
                     trans_factory=TBufferedTransportFactory())
print 'serving...'
server.serve()
