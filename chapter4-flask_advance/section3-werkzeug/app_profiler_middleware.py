# coding=utf-8
from flask import Flask
from werkzeug.contrib.profiler import ProfilerMiddleware
# 使用ProfilerMiddleware添加性能分析。当请求页面的时候，就可以获得分析的结果
# 访问页面之后，结果被保存下来：
#     ＞ ls/tmp/*.prof
#     /tmp/GET.root.000000ms.1464519481.prof
# 如果不指定profile_dir，会在终端输出分析结果

app = Flask(__name__)
app.wsgi_app = ProfilerMiddleware(app.wsgi_app)


@app.route('/')
def hello():
    return 'Hello'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
