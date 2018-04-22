# -*- coding: utf-8 -*-

import os
import pickle

import cv2
import numpy as np
from flask import current_app
from scipy.cluster.vq import kmeans, vq
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity


def get_sift(images):
    sift = cv2.xfeatures2d.SIFT_create()
    kp_all, des_all = zip(
        *[sift.detectAndCompute(img, None)for img in images]
    )
    return kp_all, des_all


def extract(uris):
    n_uris = len(uris)
    print("Extract SIFT of %d images" % n_uris)
    images = [cv2.imread(os.path.join(current_app.config['DATA_DIR'], uri))
              for uri in uris]
    # 获取每幅图的所有keypoint和对应的descriptor
    kp_all, des_all = get_sift(images)
    # 垂直堆叠所有的descriptor，每个128维
    descriptors = np.vstack(des_all)

    k = len(descriptors) // n_uris  # TODO: 选择合适的聚类数
    print("Start kmeans: %d descriptors, %d centroids" %
          (len(descriptors), k))
    # 对descriptors进行kmeans聚类，生成k个聚类中心
    centroids = kmeans(descriptors, k, 1)[0]

    # 每幅图映射每个descriptor到距其最近的聚类，统计得到关于聚类的频率向量
    freqs = [
        np.bincount(vq(des, centroids)[0], minlength=k)
        for des in des_all
    ]
    # 将聚类频率矩阵转换为已经L2归一化的tf-idf表示
    features = TfidfTransformer().fit_transform(freqs).toarray()

    with open(current_app.config['BOF_PKL'], 'wb') as bof:
        pickle.dump((uris, features, centroids), bof)


def match(uri, top_k=20):
    bof = open(current_app.config['BOF_PKL'], 'rb')
    # 读取所有图片的uri及对应feature和所有的聚类中心
    uris, features, centroids = pickle.load(bof)
    k = len(centroids)
    img = cv2.imread(os.path.join(current_app.config['DATA_DIR'], uri))
    # 计算要搜索的图像的descriptor
    des = get_sift([img])[1][0]
    # 计算要搜索的图像的聚类频率向量
    freq = np.bincount(vq(des, centroids)[0], minlength=k)
    # 将要搜索的图像的聚类频率向量转换为归一化的tf-idf表示
    feature = TfidfTransformer().fit_transform([freq]).toarray()[0]
    # 计算要搜索的图像的特征与其余所有特征的余弦相似度(每个特征已经L2归一化)
    scores = np.dot(feature, features.T)
    rank = np.argsort(-scores)[:top_k]
    images = [{'uri': uris[r], 'score': round(scores[r], 3)} for r in rank]
    return images
