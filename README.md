# sotu

利用Flask[^1]框架实现的基于内容的图像检索(Content Based Image Retrieval, CBIR)系统

## 要求

`python`版本：`3.5.2`

`pip`版本： `9.0.3`

相关组件要求见`requirements.txt`

## 初始化

程序在虚拟环境下运行，首先确保安装`virtualenv`，之后创建并激活虚拟环境，接着在虚拟环境下安装所有必要的组件，并设置相关环境变量的值.

在运行应用之前，需要提取图像特征，其中初始数据集使用的是ukbench[^2]数据集的前4096幅图，提取的特征是SIFT的改进版，即RootSIFT特征.

在Linux下所有的命令为： 

```sh
# 复制仓库并进入相应目录
$ git clone https://github.com/zysite/SoTu.git
$ cd SoTu

# 激活虚拟环境并安装所有必要的组件
$ virtualenv venv
$ . venv/bin/activate
$ pip install -r requirements.txt

# 设置环境变量FLASK_APP的值
$ export FLASK_APP=sotu.py

# 设置最大线程数
# $ export OMP_NUM_THREADS=8

# 提取图像特征
$ flask extract
```

其中激活虚拟环境的命令在Windows的环境下有所不同：

```sh
$ venv\Scripts\activate
```

如果用cmd设置环境变量，需要用`set`代替上面的`export`. 

如果用powershell设置，则命令为：

```sh
$ $env:FLASK_APP="sotu.py"
```

最后退出虚拟环境的命令为：

```sh
$ deactivate
```

## 运行

检索系统的实现基于特征袋模型(Bag of Feature, BoF)，并在此基础上利用了汉明嵌入(Hamming Embedding, HE)方法、弱几何一致性(Weak Geometric Consistency, WGC)约束和基于RANSAC算法的几何重排.

运行web应用使用下面的命令，可以指定主机和端口：

```sh
$ flask run -h localhost -p 8080
```

检索系统支持文件上传、拖拽上传和URL上传三种图片上传方式.

![demo](app/static/img/demo.gif)

## 评估

这里使用的评估指标是mAP(mean Average Precision, mAP)指标，执行评估使用下面的命令：

```sh
$ flask evaluate
```

不同方法的评价结果如下表，其中BoF模型设置的聚类数为5000，HE的阈值**ht**为23：

|      methods       |   mAP    |
| :----------------: | :------: |
|       *BoF*        | 0.713298 |
|      *BoF+HE*      | 0.878229 |
| *BoF+HE+Reranking* | 0.898573 |

Jégou提到对于ukbench数据集而言，WGC方法的效果较差[^3]，因此评估没有采用WGC方法.

## 参考文献

* Lowe D G. Distinctive image features from scale-invariant keypoints[J]. International journal of computer vision, 2004, 60(2): 91-110.
* Zisserman A. Three things everyone should know to improve object retrieval [C]. IEEE Computer Society Conference on Computer Vision and Pattern Recognition. Rhode Island, USA, 2012:2911-2918.
* Sivic J, Zisserman A. Video google: A text retrieval approach to object matching in videos [C]. IEEE International Conference on Computer Vision, 2003, 2(1470): 1470-1477.
* Jégou H, Douze M, Schmid C. Hamming Embedding and Weak Geometry Consistency for Large Scale Image Search[J]. Proc Eccv, 2008, 5302:304-317. 
* Jégou H, Douze M, Schmid C. Improving bag-of-features for large scale image search[J]. International journal of computer vision, 2010, 87(3): 316-336. 
* Zhao W L, Wu X, Ngo C W. On the Annotation of Web Videos by Efficient Near-Duplicate Search[J]. IEEE Transactions on Multimedia, 2010, 12(5):448-461.
* Philbin J, Chum O, Isard M, et al. Object retrieval with large vocabularies and fast spatial matching [C]. IEEE Conference on Computer Vision and Pattern Recognition. Minneapolis, USA, 2007: 1-8.



[^1]: http://flask.pocoo.org/docs/0.12/
[^2]: https://archive.org/download/ukbench/ukbench.zip
[^3]: https://hal.inria.fr/inria-00514760/document

