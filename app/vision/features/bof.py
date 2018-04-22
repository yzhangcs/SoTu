# -*- coding: utf-8 -*-

import os
import pickle

import cv2
import numpy as np
from flask import current_app
from scipy.cluster.vq import kmeans, vq
from sklearn.preprocessing import normalize


def get_sift(images):
    sift = cv2.xfeatures2d.SIFT_create()
    kp_all, des_all = zip(
        *[sift.detectAndCompute(img, None)for img in images]
    )
    return kp_all, des_all


def get_centroids(obs, k, iter=1):
    if os.path.exists('centroids.pkl'):
        with open('centroids.pkl', 'rb') as cen:
            centroids = pickle.load(cen)
    else:
        centroids = kmeans(obs, k, iter)[0]
        with open('centroids.pkl', 'wb') as cen:
            pickle.dump(centroids, cen)
    return centroids


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
    centroids = get_centroids(descriptors, k)
    # 每幅图映射每个descriptor到距其最近的聚类，统计得到关于聚类的频率向量
    freqs = np.array([
        np.bincount(vq(des, centroids)[0], minlength=k)
        for des in des_all
    ])
    # 计算聚类频率矩阵的tf
    tf = np.array([freq / sum(freq) for freq in freqs])
    # 计算聚类频率矩阵的idf(sklearn的实现方式)
    idf = np.log((n_uris + 1) / (np.sum((freqs > 0), axis=0) + 1)) + 1
    # 计算聚类频率矩阵的tf-idf(L2归一化)
    features = normalize(tf * idf)

    with open(current_app.config['BOF_PKL'], 'wb') as bof:
        pickle.dump((uris, features, idf, centroids), bof)


def match(uri, top_k=20):
    bof = open(current_app.config['BOF_PKL'], 'rb')
    # 读取所有图片的uri及对应feature，并读取其和所有的聚类中心
    uris, features, idf, centroids = pickle.load(bof)
    k = len(centroids)
    img = cv2.imread(os.path.join(current_app.config['DATA_DIR'], uri))
    # 计算要搜索的图像的descriptor
    des = get_sift([img])[1][0]
    # 计算要搜索的图像的聚类频率向量
    freq = np.bincount(vq(des, centroids)[0], minlength=k)
    # 计算要搜索的图像的tf
    tf = np.array([freq / sum(freq)])
    # 计算要搜索的图像的tf-idf
    feature = normalize(tf * idf)[0]
    # 计算要搜索的图像的特征与其余所有特征的余弦相似度(每个特征已经L2归一化)
    scores = np.dot(feature, features.T)
    rank = np.argsort(-scores)[:top_k]
    images = [{'uri': uris[r], 'score': round(scores[r], 3)} for r in rank]
    return images
