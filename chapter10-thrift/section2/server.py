# coding=utf-8
from pastefile.ttypes import PasteFile, UploadImageError, NotFound
from pastefile import PasteFileService
from thrift.server import TServer
from thrift.protocol import TBinaryProtocol
from thrift.transport import TTransport, TSocket
from utils import get_file_md5
from models import PasteFile as BasePasteFile
from app import app
from flask_sqlalchemy import SQLAlchemy
import os
import sys
from datetime import datetime
# 引入 thrift 包安装路径
sys.path.append('gen-py')
sys.path.append('/usr/lib/python2.7/site-packages')


db = SQLAlchemy(app)


class RealPasteFile(db.Model, BasePasteFile):
    def __init__(self, *args, **kwargs):
        BasePasteFile.__init__(self, *args, **kwargs)

    @classmethod
    def create_by_upload_file(cls, uploaded_file):
        rst = uploaded_file
        with open(rst.path) as f:
            filemd5 = get_file_md5(f)
            uploaded_file = cls.get_by_md5(filemd5)
            if uploaded_file:
                os.remove(rst.path)
                return uploaded_file
        filestat = os.stat(rst.path)
        rst.size = filestat.st_size
        rst.filemd5 = filemd5
        return rst

    def get_url(self, subtype, is_symlink=False):
        hash_or_link = self.symlink if is_symlink else self.filehash
        return 'http://%s/{subtype}/{hash_or_link}'.format(
            subtype=subtype, hash_or_link=hash_or_link)


class PasteFileHandler(object):
    # 这一步比较绕，使用Flask保存文件在app.py中执行，没有必要传输到服务端再保存，需要预先生成文件路径
    def get_file_info(self, filename, mimetype):
        rst = RealPasteFile(filename, mimetype, 0)
        return rst.filehash, rst.path

    # 方法的参数类型已经在pastefile.thrift中定义了，request是一个CreatePasteFileRequest实例
    def create(self, request):
        width = request.width
        height = request.height

        upload_file = RealPasteFile(request.filename, request.mimetype, 0,
                                    request.filehash)

        try:
            if width and height:
                paste_file = RealPasteFile.rsize(upload_file, width, height)
            else:
                paste_file = RealPasteFile.create_by_upload_file(
                    upload_file)
        except:
            raise UploadImageError()
        db.session.add(paste_file)
        db.session.commit()
        return self.convert_type(paste_file)

    def get(self, pid):
        paste_file = RealPasteFile.query.filter_by(id=pid).first()
        if not paste_file:
            raise NotFound()    # 如果不使用预先定义的异常类，抛出的异常都是 TApplicationException
        return self.convert_type(paste_file)

    @classmethod
    def convert_type(cls, paste_file):
        '''将模型转化为Thrift结构体的类型'''
        new_paste_file = PasteFile()
        for attr in ('id', 'filehash', 'filename', 'filemd5', 'uploadtime',
                     'mimetype', 'symlink', 'size', 'quoteurl', 'size', 'type',
                     'url_d', 'url_i', 'url_s', 'url_p'):
            val = getattr(paste_file, attr)
            if isinstance(val, unicode):
                # 因为需要传输字符串，所以对unicode要编码
                val = val.encode('utf-8')
            # Thrift不支持Python的时间格式，需要转换一下，在客户端再转换回来
            if isinstance(val, datetime):
                val = str(val)
            setattr(new_paste_file, attr, val)
        return new_paste_file


if __name__ == '__main__':
    import logging
    # 启动server
    logging.basicConfig()  # 这一步很重要，可以收到Thrift发出来的异常日志
    handler = PasteFileHandler()
    # Processor用来从连接中读取数据，将处理授权给handler（自己实现），最后将结果写到连接上
    processor = PasteFileService.Processor(handler)
    # 服务端使用8200端口，transport是网络读写抽象层，为到来的连接创建传输对象
    transport = TSocket.TServerSocket(port=8200)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TThreadPoolServer(
        processor, transport, tfactory, pfactory)
    print 'Starting the server...'
    server.serve()
