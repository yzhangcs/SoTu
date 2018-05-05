# sotu

利用[Flask](http://flask.pocoo.org/docs/0.12/)框架实现的基于内容的图像检索(Content Based Image Retrieval, CBIR)系统

## 要求

`python`版本：`3.5.2`

`pip`版本： `9.0.3`

相关组件要求见`requirements.txt`

## 初始化

下载仓库并进入相应目录：

```sh
$ git clone https://github.com/zy2625/SoTu.git
$ cd SoTu
```

程序在虚拟环境下运行，首先确保安装`virtualenv`，之后创建并激活虚拟环境.

在虚拟环境下需要安装所有必要的组件，并设置环境变量`FLASK_APP`的值.

在Linux下所有的命令为：

```sh
$ virtualenv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ export FLASK_APP=sotu.py
```

其中激活虚拟环境的命令在Windows的环境下有所不同：

```sh
$ venv\Scripts\activate
```

如果是用cmd设置环境变量`FLASK_APP`，需要用`set`代替上面的`export`. 

如果是用powershell设置该环境变量，则命令为：

```sh
$ $env:FLASK_APP="sotu.py"
```

## 运行

运行应用前需要提取特征.

如果数据集不存在会下载相应的数据集，数据集已存在则会遍历得到所有图片的uri.

整个提取特征的过程中会提取rootsift特征，对所有rootsift描述子进行kmeans聚类，建立倒排索引，计算tf-idf权重，并序列化保存所有的信息.

上面所有的过程由下面的命令完成：

```sh
$ flask extract
```

如果要对检索效果进行评价，可以由下面的命令完成，会得到若干幅图片的检索效果，并得到所有结果的mAP(mean Average Precision)：

```sh
$ flask evaluate
```

整个检索过程利用了汉明嵌入(Hamming Embedding, HE)、弱几何一致性(Weak Geometric Consistency, WGC)约束和基于RANSAC算法的几何重排.

运行web应用使用下面的命令，应用运行时可以指定主机和端口：

```sh
$ flask run -h localhost -p 8080
```

最后退出虚拟环境：

```sh
$ deactivate
```

## 参考
