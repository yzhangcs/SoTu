# -*- coding: utf-8 -*-

import os
import pickle

import cv2
import numpy as np
from flask import current_app
from scipy.cluster.vq import kmeans, vq
from sklearn.preprocessing import normalize

from . import he, sift


def extract(uris):
    n_uris = len(uris)
    print("Get sift features of %d images" % n_uris)
    images = [cv2.imread(os.path.join(current_app.config['DATA_DIR'], uri))
              for uri in uris]
    # 获取每幅图的所有keypoint和对应的descriptor
    keypoints, descriptors = sift.extract(images)
    # 垂直堆叠所有的descriptor，每个128维
    des_all = np.vstack(descriptors)

    k = 1000  # TODO: 选择合适的聚类数
    print("Start kmeans with %d descriptors and %d centroids" %
          (len(des_all), k))
    # 对descriptors进行kmeans聚类，生成k个聚类中心
    centroids = kmeans(des_all, k, 1)[0]

    # 获取HE投影矩阵
    P = he.get_proj_matrix(64, 128)
    # 根据投影矩阵对每幅图的所有descriptor降维
    projections = [np.dot(des, P.T) for des in descriptors]
    # 映射每幅图的每个descriptor到距其最近的聚类并得到该聚类的索引
    indices = [vq(des, centroids)[0] for des in descriptors]
    # 得到k*64的中值矩阵
    medians = he.get_medians(np.vstack(projections), np.vstack(indices), k)
    # 得到每幅图的每个descriptor对应的Hamming编码
    binaries = [he.get_binary(prj, idx, medians)
                for idx, des in zip(indices, projections)]

    # 统计得到关于聚类的频率向量
    freqs = np.array([np.bincount(idx, minlength=k) for idx in idx_all])
    # 计算聚类频率矩阵的idf(sklearn的实现方式)
    idf = np.log((freqs.shape[0] + 1) / (np.sum((freqs > 0), axis=0) + 1)) + 1

    bof_path = os.path.join(current_app.config['FEATURE_DIR'], 'bof.pkl')
    with open(bof_path, 'wb') as bof_pkl:
        pickle.dump((uris, indices, binaries, idf, centroids, P, medians),
                    bof_pkl)


def match(uri, top_k=20):
    bof_path = os.path.join(current_app.config['FEATURE_DIR'], 'bof.pkl')
    bof_pkl = open(bof_path, 'rb')
    uris, indices, binaries, idf, centroids, P, medians = pickle.load(bof_pkl)

    k = len(centroids)
    img = cv2.imread(os.path.join(current_app.config['DATA_DIR'], uri))
    # 计算要搜索的图像的所有descriptor
    des = sift.extract([img])[1][0]
    # 根据投影矩阵对要搜索的图像的所有descriptor降维
    prj = np.dot(des, P.T)
    # 映射要搜索的图像的所有descriptor到距其最近的聚类并得到该聚类的索引
    idx = vq(des, centroids)[0]
    # 计算要搜索的图像的所有descriptor对应的Hamming编码
    binary = he.get_binary(prj, idx, medians)

    # 定义Hamming阈值
    threshold = 25
    scores = [get_scores(idx, i, threshold, binary, b, idf)
              for i, b in indices, binaries]
    rank = np.argsort(-scores)[: top_k]
    images = [uris[r] for r in rank]
    return images
