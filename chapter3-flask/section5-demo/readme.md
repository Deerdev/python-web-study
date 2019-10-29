# 文件托管服务

- 上传后的文件可以被永久存放。
- 上传后的文件有一个功能完备的预览页。预览页显示文件大小、文件类型、上传时间、下载地址和短链接等信息。
- 可以通过传参数对图片进行缩放和剪切。
- 不错的页面展示效果。
- 为节省空间，相同文件不重复上传，如果文件已经上传过，则直接返回之前上传的文件。

安装依赖：

```shell
sudo apt-get install libjpeg8-dev-yq
pip install-r chapter3/section5/requirements.txt
```

基本依赖：

- python-magic：libmagic的Python绑定，用于确定文件类型。
- Pillow：PIL（Python Imaging Library）的分支，用来替代PIL。
- cropresize2：用来剪切和调整图片大小。
- short_url：创建短链接。

文件说明:

- `databases/schema.sql`： 建表语句

导入数据看 r 中：

```shell
＞ (echo"use r";cat databases/schema.sql)|mysql --user='web' --password='web'
```

- config.py：用于存放配置
- utils.py：用于存放功能函数
- mimes.py：只接受文件中定义了的媒体类型
- ext.py：存放扩展的封装
- models.py：存放模型
- app.py：应用主程序



