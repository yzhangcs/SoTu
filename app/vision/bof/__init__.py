# -*- coding: utf-8 -*-

import os
import pickle

import cv2
import numpy as np
from flask import current_app
from scipy.cluster.vq import kmeans, vq
from sklearn.preprocessing import normalize

from . import sift


def extract(uris):
    n_uris = len(uris)
    print("Get sift features of %d images" % n_uris)
    images = [cv2.imread(os.path.join(current_app.config['DATA_DIR'], uri))
              for uri in uris]
    # 获取每幅图的所有keypoint和对应的descriptor
    keypoints, descriptors = sift.extract_all(images)
    # 垂直堆叠所有的descriptor，每个128维
    des_all = np.vstack(descriptors)

    k = 1000  # TODO: 选择合适的聚类数
    print("Start kmeans with %d descriptors and %d centroids" %
          (len(des_all), k))
    # 对descriptors进行kmeans聚类，生成k个聚类中心
    centroids = kmeans(des_all, k, 1)[0]

    # 映射每幅图的每个descriptor到距其最近的聚类并得到该聚类的索引
    labels = [vq(des, centroids)[0] for des in descriptors]
    # 每幅图映射每个descriptor到距其最近的聚类，统计得到关于聚类的频率向量
    freqs = np.array([np.bincount(lbl, minlength=k) for lbl in labels])
    # 计算聚类频率矩阵的idf(sklearn的实现方式)
    idf = np.log((freqs.shape[0] + 1) / (np.sum((freqs > 0), axis=0) + 1)) + 1
    # 计算聚类频率矩阵的tf-idf(L2归一化)
    features = normalize(freqs * idf)

    bof_path = os.path.join(current_app.config['FEATURE_DIR'], 'bof.pkl')
    with open(bof_path, 'wb') as bof_pkl:
        pickle.dump((uris, features, idf, centroids), bof_pkl)


def match(uri, top_k=20):
    bof_path = os.path.join(current_app.config['FEATURE_DIR'], 'bof.pkl')
    bof_pkl = open(bof_path, 'rb')
    # 读取所有图片的uri及对应feature，并读取其和所有的聚类中心
    uris, features, idf, centroids = pickle.load(bof_pkl)

    k = len(centroids)
    img = cv2.imread(os.path.join(current_app.config['DATA_DIR'], uri))
    # 计算要搜索的图像的所有descriptor
    des = sift.extract(img)[1]
    # 映射要搜索的图像的所有descriptor到距其最近的聚类并得到该聚类的索引
    lbl = vq(des, centroids)[0]
    # 计算要搜索的图像的聚类频率向量
    freq = np.bincount(lbl, minlength=k)
    # 计算要搜索的图像的tf-idf
    feature = normalize([freq * idf])[0]
    # 计算要搜索的图像的特征与其余所有特征的余弦相似度(每个特征已经L2归一化)
    scores = np.dot(feature, features.T)

    rank = np.argsort(-scores)[:top_k]
    images = [uris[r] for r in rank]
    return images
