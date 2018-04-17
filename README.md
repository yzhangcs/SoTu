# sotu

利用[Flask](http://flask.pocoo.org/docs/0.12/)框架实现的基于内容的图像检索(Content Based Image Retrieval, CBIR)系统

## 要求

`python`版本：`3.5.2`

`pip`版本： `9.0.3`

相关组件要求见`requirements.txt`

## 浏览器兼容

由于使用了部分HTML5的特性，因此仅支持现代浏览器，IE9及以下的浏览器可能会有显示问题. 此外由于对于input元素中files属性安全性政策执行的不同，部分浏览器的「Drag & Drop」功能会受影响，相关情况见[W3C testing](https://github.com/w3c/web-platform-tests/pull/6617).  
页面显示及各项功能在新版本的Chrome、FireFox及Edge上经测试没有问题.

## 初始化

下载仓库并进入相应目录：

```sh
$ git clone https://github.com/zy2625/SoTu.git
$ cd SoTu
```

### 虚拟环境

首先安装`virtualenv`，创建并激活虚拟环境. 

在Linux下：

```sh
$ pip install --user virtualenv
$ virtualenv venv
$ . venv/bin/activate
```

在Windows下：

```sh
$ pip install virtualenv
$ virtualenv venv
$ venv\Scripts\activate
```

在虚拟环境下安装必要组件：

```sh
$ pip install -r requirements.txt
```

在运行应用之前，需要设置环境变量`FLASK_APP`的值，在bash下：

```sh
$ export FLASK_APP=sotu.py
```

如果是cmd，用`set`代替上面的`export`. 

在powershell下：

```sh
$ $env:FLASK_APP="sotu.py"
```

### 数据库

这里用[Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.3/)管理数据库，用[Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/)来维护数据库迁移，初次运行需要重新生成数据库：

```sh
$ flask db upgrade
```

数据库中插入[Caltech101](http://www.vision.caltech.edu/Image_Datasets/Caltech101/)作为初始的数据集，可以用`flask shell`命令进入shell会话并执行下面的操作：

```sh
>>> Image.insert_caltech101()
>>> Image.query.count()
9144
>>> exit()
```

## 运行

运行应用时可以指定主机和端口：

```sh
$ flask run -h localhost -p 8080
```

最后退出虚拟环境：

```sh
$ deactivate
```

## 相关链接
[Explore Flask — Explore Flask 1.0 documentation](http://exploreflask.com/en/latest/index.html)  
[关于Flask表单，我所知道的一切](https://zhuanlan.zhihu.com/p/23577026?refer=flask)  
[Flask-WTF：单个页面两个（多个）表单](https://zhuanlan.zhihu.com/p/23437362)  
[CSRF Protection](http://flask-wtf.readthedocs.io/en/stable/csrf.html)  
[Flask: show flash messages in alertbox](https://stackoverflow.com/questions/33580143/flask-show-flash-messages-in-alertbox)  
[How to make this Header/Content/Footer layout using CSS?](https://stackoverflow.com/questions/7123138/how-to-make-this-header-content-footer-layout-using-css)  
[Drag and Drop File Upload jQuery Example](http://hayageek.com/drag-and-drop-file-upload-jquery/)  
[How to set file input value when dropping file on page?](https://stackoverflow.com/questions/47515232/how-to-set-file-input-value-when-dropping-file-on-page)  
[使用纯 CSS 实现 Google Photos 照片列表布局](https://github.com/xieranmaya/blog/issues/4)  
[window.onload vs document.onload](https://stackoverflow.com/questions/588040/window-onload-vs-document-onload)  
[Targeting flex items on the last row](https://stackoverflow.com/questions/42176419/targeting-flex-items-on-the-last-row)  
[Image inside div has extra space below the image](https://stackoverflow.com/questions/5804256/image-inside-div-has-extra-space-below-the-image)  
[How TO - Image Overlay Title](https://www.w3schools.com/howto/howto_css_image_overlay_title.asp)  


