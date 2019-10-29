# coding=utf-8
import os

from werkzeug import SharedDataMiddleware
from flask import abort, Flask, request, jsonify, redirect, send_file

# 只是把第三方扩展初始化放在了app.py中，而没有使用“db=SQLAlchemy(app)”这样的方式。这是因为在大型应用中如果db被多个模型文件引用的话，会造成“from app import db”这样的方式，但是往往也在app.py中也会引用模型文件定义的类，这就造成了循环引用。所以最好的做法是把它放在不依赖其他模块的独立文件中。
from ext import db, mako, render_template
from models import PasteFile
from utils import get_file_path, humanize_bytes

ONE_MONTH = 60 * 60 * 24 * 30

app = Flask(__name__, template_folder='../../templates/r',
            static_folder='../../static')
app.config.from_object('config')

# 使用SharedDataMiddleware是实现在页面读取源文件的最简单的方法
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/i/': get_file_path()
})

mako.init_app(app)
db.init_app(app)

# 支持对现有的图片重新设置大小，返回新的图片地址
@app.route('/r/<img_hash>')
def rsize(img_hash):
    w = request.args['w']
    h = request.args['h']

    # 其中get_by_filehash方法就是从数据库中找到匹配filehash的条目
    old_paste = PasteFile.get_by_filehash(img_hash)
    new_paste = PasteFile.rsize(old_paste, w, h)
    # url_i属性获取的是源文件的地址
    return new_paste.url_i

# 下载文件时使用“/d/img_hash.jpg”这样的地址，可以用Flask提供的send_file实现
@app.route('/d/<filehash>', methods=['GET'])
def download(filehash):
    paste_file = PasteFile.get_by_filehash(filehash)

    return send_file(open(paste_file.path, 'rb'),
                     mimetype='application/octet-stream',
                     cache_timeout=ONE_MONTH,
                     as_attachment=True,
                     attachment_filename=paste_file.filename.encode('utf-8'))

# 首页，通过这个页面可以上传图片，并生成预览页
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        w = request.form.get('w')
        h = request.form.get('h')
        if not uploaded_file:
            return abort(400)

        if w and h:
            # 如果上传请求是一个POST请求，并且指定了长和宽，会先裁剪图片再保存
            paste_file = PasteFile.rsize(uploaded_file, w, h)
        else:
            paste_file = PasteFile.create_by_upload_file(uploaded_file)
        db.session.add(paste_file)
        db.session.commit()

        return jsonify({
            'url_d': paste_file.url_d,
            'url_i': paste_file.url_i,
            'url_s': paste_file.url_s,
            'url_p': paste_file.url_p,
            'filename': paste_file.filename,
            'size': humanize_bytes(paste_file.size),
            'time': str(paste_file.uploadtime),
            'type': paste_file.type,
            'quoteurl': paste_file.quoteurl
        })
    # get
    return render_template('index.html', **locals())


@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@app.route('/j', methods=['POST'])
def j():
    uploaded_file = request.files['file']

    if uploaded_file:
        paste_file = PasteFile.create_by_upload_file(uploaded_file)
        db.session.add(paste_file)
        db.session.commit()
        width, height = paste_file.image_size

        return jsonify({
            'url': paste_file.url_i,
            'short_url': paste_file.url_s,
            'origin_filename': paste_file.filename,
            'hash': paste_file.filehash,
            'width': width,
            'height': height
        })

    return abort(400)

# 预览文件使用“/p/img_hash.jpg”这样的地址
@app.route('/p/<filehash>')
def preview(filehash):
    paste_file = PasteFile.get_by_filehash(filehash)

    if not paste_file:
        filepath = get_file_path(filehash)
        if not(os.path.exists(filepath) and (not os.path.islink(filepath))):
            return abort(404)

        paste_file = PasteFile.create_by_old_paste(filehash)
        db.session.add(paste_file)
        db.session.commit()

    return render_template('success.html', p=paste_file)

# 由于文件hash值太长，支持使用短连接的方式访问，使用“/s/short_url”这样的地址
# 但是并不需要把短链接存放进数据库，正确的做法是用id这个唯一标识生成短链接地址
@app.route('/s/<symlink>')
def s(symlink):
    paste_file = PasteFile.get_by_symlink(symlink)

    return redirect(paste_file.url_p)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
