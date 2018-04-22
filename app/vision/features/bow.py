# -*- coding: utf-8 -*-

import os
import pickle

import cv2
import numpy as np
from flask import current_app
from scipy.cluster.vq import kmeans, vq
from sklearn.preprocessing import normalize


def get_sift(images):
    sift_path = os.path.join(current_app.config['FEATURE_DIR'], 'sift.pkl')
    if os.path.exists(sift_path):
        with open(sift_path, 'rb') as s:
            kp_all, des_all = pickle.load(s)
    else:
        sift = cv2.xfeatures2d.SIFT_create()
        kp_all, des_all = zip(
            *[sift.detectAndCompute(img, None) for img in images]
        )
        with open(sift_path, 'wb') as s:
            pickle.dump((kp_all, des_all), s)
    return kp_all, des_all


def get_centroids(obs, k, iter=1):
    cen_path = os.path.join(current_app.config['FEATURE_DIR'], 'cen.pkl')
    if os.path.exists(cen_path):
        with open(cen_path, 'rb') as cen:
            centroids = pickle.load(cen)
    else:
        centroids = kmeans(obs, k, iter)[0]
        with open(cen_path, 'wb') as cen:
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

    bow_path = os.path.join(current_app.config['FEATURE_DIR'], 'bow.pkl')
    with open(bow_path, 'wb') as bow:
        pickle.dump((uris, features, idf, centroids), bow)


def match(uri, top_k=20):
    bow_path = os.path.join(current_app.config['FEATURE_DIR'], 'bow.pkl')
    bow = open(bow_path, 'rb')
    # 读取所有图片的uri及对应feature，并读取其和所有的聚类中心
    uris, features, idf, centroids = pickle.load(bow)
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
