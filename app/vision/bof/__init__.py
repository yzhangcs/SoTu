# -*- coding: utf-8 -*-

import os
import pickle

import cv2
import numpy as np
from flask import current_app
from sklearn.cluster import MiniBatchKMeans

from . import he
from .rootsift import RootSIFT


# class BoF(object):
#     def __init__(self, uris):
#         self.n_uris = len(uris)
#         self.n_clusters = 2000
#         self.sift_path = os.path.join(
#             current_app.config['FEATURE_DIR'], 'sift.pkl')
#         self.inv_path = os.path.join(
#             current_app.config['FEATURE_DIR'], 'inv.pkl')
#         self.bof_path = os.path.join(
#             current_app.config['FEATURE_DIR'], 'bof.pkl')

#     def load_rootsift(self):
#         pass


def extract(uris):
    n_uris = len(uris)
    sift_path = os.path.join(current_app.config['FEATURE_DIR'], 'sift.pkl')
    inv_path = os.path.join(current_app.config['FEATURE_DIR'], 'inv.pkl')
    bof_path = os.path.join(current_app.config['FEATURE_DIR'], 'bof.pkl')
    images = [cv2.imread(os.path.join(current_app.config['DATA_DIR'], uri))
              for uri in uris]

    print("Get rootsift features of %d images" % n_uris)
    if os.path.exists(sift_path):
        with open(sift_path, 'rb') as sift_pkl:
            tmps, descriptors = pickle.load(sift_pkl)
            keypoints = [
                [cv2.KeyPoint(x=tmp[0][0], y=tmp[0][1], _size=tmp[1],
                              _angle=tmp[2], _response=tmp[3],
                              _octave=tmp[4], _class_id=tmp[5])
                 for t in tmp]
                for tmp in tmps
            ]
    else:
        # 获取每幅图的所有keypoint和对应的descriptor
        rootsift = RootSIFT()
        keypoints, descriptors = zip(
            *[rootsift.extract(img) for img in images]
        )
        tmps = [
            [(k.pt, k.size, k.angle, k.response,
              k.octave, k.class_id) for k in kp]
            for kp in keypoints
        ]
        with open(sift_path, 'wb') as sift_pkl:
            pickle.dump((tmps, descriptors), sift_pkl)
    lens = [len(des) for des in descriptors]

    n_clusters = 2000  # TODO: 选择合适的聚类数
    # 垂直堆叠所有的descriptor，每个128维
    des_all = np.vstack([des for des in descriptors if des is not None])
    print("Start kmeans with %d descriptors and %d centroids" %
          (len(des_all), n_clusters))
    # 对descriptors进行kmeans聚类，生成k个聚类中心
    kmeans = MiniBatchKMeans(
        n_clusters=n_clusters, batch_size=1000, init_size=n_clusters * 3
    ).fit(des_all)
    # 映射每幅图的每个descriptor到距其最近的聚类并得到该聚类的索引
    labels = [kmeans.predict(des) for des in descriptors]

    print("Porject %d descriptors from 128d to 64d" % len(des_all))
    # 生成128 * 128的符合标准正态分布的随机矩阵
    M = np.random.randn(128, 128)
    # QR分解得到正交矩阵Q
    Q, R = np.linalg.qr(M)
    # 获取64*128投影矩阵
    P = Q[:64, :]
    # 根据投影矩阵对每幅图的所有descriptor降维
    projections = [np.dot(des, P.T) for des in descriptors]

    print("Get medians of %d visual words" % n_clusters)
    # 得到k*64的中值矩阵
    medians = he.get_medians(np.vstack(projections),
                             np.hstack(labels), n_clusters)

    print("Get binary signatures of %d descriptors" % len(des_all))
    # 得到每幅图的每个descriptor对应的Hamming编码
    binaries = [
        [he.bitspack(p > medians[l]) for p, l in zip(prj, label)]
        for prj, label in zip(projections, labels)
    ]
    # 建立聚类的倒排索引，每个条目包含median和所有属于这个聚类的特征对应的图片id及Hamming编码
    entries = [{'median': md, 'ids': []} for md in medians]
    for i, (kp, binary, label) in enumerate(zip(keypoints, binaries, labels)):
        for k, b, l in zip(kp, binary, label):
            entries[l]['ids'].append(
                (i, np.radians(k.angle), np.log2(k.octave), b)
            )
    with open(inv_path, 'wb') as inv_pkl:
        pickle.dump(entries, inv_pkl)

    # 每幅图映射每个descriptor到距其最近的聚类，统计得到关于聚类的频率向量
    freqs = np.array([np.bincount(label, minlength=n_clusters)
                      for label in labels])
    # 计算聚类频率矩阵的idf(sklearn的实现方式)
    idf = np.log((freqs.shape[0] + 1) / (np.sum((freqs > 0), axis=0) + 1)) + 1

    with open(bof_path, 'wb') as bof_pkl:
        pickle.dump((uris, lens, idf, kmeans, P), bof_pkl)


def match(uri, top_k=20, reranking=5):
    bof_path = os.path.join(current_app.config['FEATURE_DIR'], 'bof.pkl')
    inv_path = os.path.join(current_app.config['FEATURE_DIR'], 'inv.pkl')
    bof_pkl = open(bof_path, 'rb')
    inv_pkl = open(inv_path, 'rb')
    # 读取所有图片的uri及对应feature，并读取其和所有的聚类中心
    uris, lens, idf, kmeans, P = pickle.load(bof_pkl)
    entries = pickle.load(inv_pkl)

    n_clusters = idf.shape[0]
    img = cv2.imread(os.path.join(current_app.config['DATA_DIR'], uri))
    # 计算要搜索的图像的所有descriptor
    kp, des = RootSIFT().extract(img)
    # 计算每个keypoint对应的关于角度和尺度的几何信息
    geom = [(np.radians(k.angle), np.log2(k.octave)) for k in kp]
    # 映射要搜索的图像的所有descriptor到距其最近的聚类并得到该聚类的索引
    label = kmeans.predict(des)

    # 根据投影矩阵对要搜索的图像的所有descriptor降维
    prj = np.dot(des, P.T)
    # 计算要搜索的图像的所有descriptor对应的Hamming编码
    binary = [he.bitspack(p > entries[l]['median'])
              for p, l in zip(prj, label)]

    # 定义Hamming阈值
    threshold = 25
    print("Start to score all iamges")
    weights = [[] for i in range(len(uris))]
    angle_diffs = [[] for i in range(len(uris))]
    scale_diffs = [[] for i in range(len(uris))]
    for bin_q, lbl_q, (ang_q, sca_q) in zip(binary, label, geom):
        for img_id, ang_t, sca_t, bin_t in entries[lbl_q]['ids']:
            if he.distance(bin_q, bin_t) < threshold:
                angle_diffs[img_id].append(
                    np.arctan2(np.sin(ang_q - ang_t), np.cos(ang_q - ang_t))
                )
                scale_diffs[img_id].append(sca_q - sca_t)
                weights[img_id].append(idf[lbl_q])
    angle_scores = [
        max(np.histogram(ad, bins=8, range=(-np.pi, np.pi), weights=w)[0])
        for ad, w in zip(angle_diffs, weights)
    ]
    scale_scores = [
        max(np.histogram(sd, bins=8, range=(-5, 5), weights=w)[0])
        for sd, w in zip(scale_diffs, weights)
    ]
    scores = np.array([min(a, s) for a, s in zip(angle_scores, scale_scores)])
    scores = scores / lens

    rank = np.argsort(-scores)
    images = [uris[r] for r in rank[:top_k]]
    return images
