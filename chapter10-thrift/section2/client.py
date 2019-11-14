# coding=utf-8
# 为了让客户端连接发生在服务器启动之后，而且能重用连接，我们使用了LocalProxy包装client：
from werkzeug.local import LocalProxy
from pastefile.ttypes import (
    PasteFile, CreatePasteFileRequest, UploadImageError,
    NotFound)
from pastefile import PasteFileService
from thrift.protocol import TBinaryProtocol
from thrift.transport import TTransport, TSocket
import sys

sys.path.append('gen-py')
sys.path.insert(0, '/usr/lib/python2.7/site-packages')


# 启动客户端
def get_client():
    # 同样使用8200端口，使用阻塞式I/O进行传输，是最常见的模式
    transport = TSocket.TSocket('localhost', 8200)
    transport = TTransport.TBufferedTransport(transport)
    # 封装协议，使用二进制编码格式进行数据传输
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = PasteFileService.Client(protocol)
    transport.open()    # 打开连接
    return client


client = LocalProxy(get_client)

# 由于上传逻辑出现在两个视图中，所以抽象一个连接函数，让代码复用：


def create(uploaded_file, width=None, height=None):
    filename = uploaded_file.filename.encode('utf-8')
    mimetype = uploaded_file.mimetype.encode('utf-8')
    filehash, path = client.get_file_info(filename, mimetype)

    create_request = CreatePasteFileRequest()

    create_request.filename = filename
    create_request.mimetype = mimetype
    create_request.filehash = filehash
    # 接收上传文件，直接保存，没有必要传输到服务端再去保存
    uploaded_file.save(path)
    if width is not None and height is not None:
        create_request.width = width
        create_request.height = height
    try:
        pastefile = client.create(create_request)
    except UploadImageError:    # 异常是在PasteFileHandler的create方法中预先定义的
        return {'r': 1, 'error': 'upload fail'}

    print isinstance(pastefile, PasteFile)  # 只是验证

    try:    # 事实上没有必要重新get一次，因为create方法已经返回了PasteFile实例，这里 只是演示
        paste_file = client.get(pastefile.id)
    except NotFound:
        return {'r': 1, 'error': 'not found'}

    return {'r': 0, 'paste_file': paste_file}
