# coding=utf-8
from flask import Flask, g

app = Flask(__name__)
app.config['SERVER_NAME'] = 'example.com:9000'


@app.url_value_preprocessor
def get_site(endpoint, values):
    g.site = values.pop('subdomain')


@app.route('/', subdomain='<subdomain>')
def index():
    return g.site


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)

# 在虚拟机上绑定一下域名，也就是在/etc/hosts添加一行：
    # 127.0.0.1 a.example.com b.example.com
# 现在验证它：
    # 支持 subdomain 的访问
    # ＞ http http://b.example.com:9000 --print b # b表示只输出响应的主体
    # b
