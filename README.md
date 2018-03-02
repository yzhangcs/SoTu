# sotu

基于`Flask`框架的图像识别系统

## 要求

1. `Python`版本

```
Python 3.5.2
```

2. 相关组件要求

```
Flask >= 0.12.2
Flask-WTF >= 0.14
Jinja2 >= 2.9.6
Werkzeug >= 0.12.2
```

## 浏览器兼容

由于使用了部分`HTML5`的特性，因此仅支持现代浏览器，IE9及以下的浏览器可能会有显示问题. 此外由于对于`input`元素中`files`属性安全性政策执行的不同，部分浏览器的「`Drag & Drop`」功能会受影响，相关情况见[W3C testing](https://github.com/w3c/web-platform-tests/pull/6617).  
页面显示及各项功能在新版本的`Chrome`、`FireFox`及`Edge`上经测试没有问题.

## 运行

1. Clone

```sh
$ git clone https://github.com/zy2625/SoTu.git
```

2. Activate

* Linux:
```sh
$ cd SoTu
$ sudo pip install virtualenv
$ virtualenv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

* Windows: 
```sh
$ cd SoTu
$ pip install virtualenv
$ virtualenv venv
$ venv\Scripts\activate
$ pip install -r requirements.txt
```

3. Run

* bash

```sh
$ export FLASK_APP=sotu.py
$ flask run -h localhost -p 8080
```

* powershell

```sh
$ $env:FLASK_APP="sotu.py"
$ flask run -h localhost -p 8080
```

* cmd

```sh
$ set FLASK_APP=sotu.py
$ flask run -h localhost -p 8080
```

4. Deactivate

```sh
$ deactivate
```

## 相关链接
[Welcome to Flask](http://flask.pocoo.org/docs/0.12/)  
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