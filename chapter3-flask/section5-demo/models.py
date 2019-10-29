# coding=utf-8
import os
import uuid
import magic
from datetime import datetime

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

import cropresize2
import short_url
from PIL import Image
from flask import abort, request
from werkzeug.utils import cached_property

from mimes import IMAGE_MIMES, AUDIO_MIMES, VIDEO_MIMES
from utils import get_file_md5, get_file_path
from ext import db


class PasteFile(db.Model):
    __tablename__ = 'PasteFile'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(5000), nullable=False)
    filehash = db.Column(db.String(128), nullable=False, unique=True)
    filemd5 = db.Column(db.String(128), nullable=False, unique=True)
    uploadtime = db.Column(db.DateTime, nullable=False)
    mimetype = db.Column(db.String(256), nullable=False)
    size = db.Column(db.Integer, nullable=False)

    def __init__(self, filename='', mimetype='application/octet-stream',
                 size=0, filehash=None, filemd5=None):
        self.uploadtime = datetime.now()
        self.mimetype = mimetype
        self.size = int(size)
        self.filehash = filehash if filehash else self._hash_filename(filename)
        self.filename = filename if filename else self.filehash
        self.filemd5 = filemd5

    @staticmethod
    def _hash_filename(filename):
        _, _, suffix = filename.rpartition('.')
        return '%s.%s' % (uuid.uuid4().hex, suffix)

    @cached_property
    def symlink(self):
        # 短链接 使用 id
        return short_url.encode_url(self.id)

    @classmethod
    def get_by_symlink(cls, symlink, code=404):
        # 解出短链 id
        id = short_url.decode_url(symlink)
        return cls.query.filter_by(id=id).first() or abort(code)

    @classmethod
    def get_by_filehash(cls, filehash, code=404):
        return cls.query.filter_by(filehash=filehash).first() or abort(code)

    @classmethod
    def get_by_md5(cls, filemd5):
        return cls.query.filter_by(filemd5=filemd5).first()

    @classmethod
    def create_by_upload_file(cls, uploaded_file):
        rst = cls(uploaded_file.filename, uploaded_file.mimetype, 0)
        # 创建PasteFile实例前会先保存文件，保存的文件名是rst.path。如果通过被上传文件的md5值判断的文件之前已经上传过，则直接删掉这个文件，并返回之前创建的文件
        uploaded_file.save(rst.path)
        with open(rst.path, 'rb') as f:
            filemd5 = get_file_md5(f)
            uploaded_file = cls.get_by_md5(filemd5)
            if uploaded_file:
                os.remove(rst.path)
                return uploaded_file
        filestat = os.stat(rst.path)
        rst.size = filestat.st_size
        rst.filemd5 = filemd5
        return rst

    @classmethod
    def create_by_old_paste(cls, filehash):
        filepath = get_file_path(filehash)
        mimetype = magic.from_file(filepath, mime=True)
        filestat = os.stat(filepath)
        size = filestat.st_size

        rst = cls(filehash, mimetype, size, filehash=filehash)
        return rst

    @property
    def path(self):
        # rst.path使用了filehash，filehash是通过_hash_filename方法生成的随机名字，这是为了防止不同的用户上传的同名文件造成的替换
        return get_file_path(self.filehash)

    def get_url(self, subtype, is_symlink=False):
        hash_or_link = self.symlink if is_symlink else self.filehash
        return 'http://{host}/{subtype}/{hash_or_link}'.format(
            subtype=subtype, host=request.host, hash_or_link=hash_or_link)

    @property
    def url_i(self):
        return self.get_url('i')

    # 文件预览地址
    @property
    def url_p(self):
        return self.get_url('p')
    # 文件短链接地址
    @property
    def url_s(self):
        return self.get_url('s', is_symlink=True)
    # 文件下载地址
    @property
    def url_d(self):
        return self.get_url('d')

    @property
    def image_size(self):
        if self.is_image:
            f = open(self.path, 'rb')
            im = Image.open(f)
            return im.size
        return (0, 0)

    @property
    def quoteurl(self):
        return quote(self.url_i)

    # 如果上传请求是一个POST请求，并且指定了长和宽，会先裁剪图片再保存
    @classmethod
    def rsize(cls, old_paste, weight, height):
        assert old_paste.is_image, TypeError('Unsupported Image Type.')
        f = open(old_paste.path, 'rb')
        im = Image.open(f)

        img = cropresize2.crop_resize(im, (int(weight), int(height)))

        rst = cls(old_paste.filename, old_paste.mimetype, 0)
        img.save(rst.path)
        filestat = os.stat(rst.path)
        rst.size = filestat.st_size
        return rst

    @property
    def is_image(self):
        return self.mimetype in IMAGE_MIMES

    @property
    def is_audio(self):
        return self.mimetype in AUDIO_MIMES

    @property
    def is_video(self):
        return self.mimetype in VIDEO_MIMES

    @property
    def is_pdf(self):
        return self.mimetype == 'application/pdf'

    @property
    def type(self):
        for t in ('image', 'pdf', 'video', 'audio'):
            if getattr(self, 'is_' + t):
                return t
        return 'binary'
