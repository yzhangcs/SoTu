# -*- coding: utf-8 -*-

import cv2
import numpy as np
from scipy.cluster.vq import kmeans, vq
from sklearn.feature_extraction.text import TfidfTransformer


def get_sift(images):
    sift = cv2.xfeatures2d.SIFT_create()
    kp_all, des_all = zip(*[
        sift.detectAndCompute(images, None) for img in images
    ])
    return kp_all, des_all


def get_features(uris):
    n_uris = len(uris)

    print("Extract SIFT of %d images" % n_uris)
    images = [cv2.imread(uri) for uri in uris]
    # 获取每幅图的所有keypoint和对应的descriptor
    kp_all, des_all = get_sift(images)
    # 垂直堆叠所有的descriptor，每个128维
    descriptors = np.vstack(des_all)

    k = len(descriptors) // n_uris  # TODO: 选择合适的聚类数
    print("Start kmeans: %d descriptors, %d centroids" %
          (len(descriptors), k))
    # 对descriptors进行kmeans聚类，生成k个聚类中心
    centroids = kmeans(descriptors, k, 1)[0]

    # 每幅图映射每个descriptor到距其最近的聚类，统计得到一个关于聚类的频率矢量
    freqs = [
        np.bincount(vq(des, centroids)[0], minlength=k)
        for des in des_all
    ]
    # 将聚类频率矩阵转换为归一化的tf-idf表示
    features = TfidfTransformer().fit_transform(freqs).toarray()
    return descriptors, features
