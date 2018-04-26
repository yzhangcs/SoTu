# -*- coding: utf-8 -*-

import os
import pickle

import cv2
import numpy as np
from flask import current_app
from sklearn.cluster import MiniBatchKMeans

from .rootsift import RootSIFT
from . import he


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
            descriptors = pickle.load(sift_pkl)
    else:
        # 获取每幅图的所有keypoint和对应的descriptor
        keypoints, descriptors = RootSIFT().extract_all(images)
        with open(sift_path, 'wb') as sift_pkl:
            pickle.dump(descriptors, sift_pkl)
    lens = [len(des) for des in descriptors]

    k = 2000  # TODO: 选择合适的聚类数
    # 垂直堆叠所有的descriptor，每个128维
    des_all = np.vstack(descriptors)
    print("Start kmeans with %d descriptors and %d centroids" %
          (len(des_all), k))
    # 对descriptors进行kmeans聚类，生成k个聚类中心
    kmeans = MiniBatchKMeans(
        n_clusters=k, batch_size=1000, init_size=k * 3
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

    print("Get medians of %d visual words" % k)
    # 得到k*64的中值矩阵
    medians = he.get_medians(np.vstack(projections), np.hstack(labels), k)

    print("Get binary signatures of %d descriptors" % len(des_all))
    # 得到每幅图的每个descriptor对应的Hamming编码
    binaries = [
        [he.bitspack(p > medians[l]) for p, l in zip(prj, label)]
        for prj, label in zip(projections, labels)
    ]
    # 建立聚类的倒排索引，每个条目包含median和所有属于这个聚类的特征对应的图片id及Hamming编码
    entries = [{'median': md, 'img_ids': []} for md in medians]
    for img_id, (binary, label) in enumerate(zip(binaries, labels)):
        for b, l in zip(binary, label):
            entries[l]['img_ids'].append((img_id, b))
    with open(inv_path, 'wb') as inv_pkl:
        pickle.dump(entries, inv_pkl)

    # 每幅图映射每个descriptor到距其最近的聚类，统计得到关于聚类的频率向量
    freqs = np.array([np.bincount(label, minlength=k) for label in labels])
    # 计算聚类频率矩阵的idf(sklearn的实现方式)
    idf = np.log((freqs.shape[0] + 1) / (np.sum((freqs > 0), axis=0) + 1)) + 1

    with open(bof_path, 'wb') as bof_pkl:
        pickle.dump((uris, lens, idf, kmeans, P), bof_pkl)


def match(uri, top_k=20):
    bof_path = os.path.join(current_app.config['FEATURE_DIR'], 'bof.pkl')
    inv_path = os.path.join(current_app.config['FEATURE_DIR'], 'inv.pkl')
    bof_pkl = open(bof_path, 'rb')
    inv_pkl = open(inv_path, 'rb')
    # 读取所有图片的uri及对应feature，并读取其和所有的聚类中心
    uris, lens, idf, kmeans, P = pickle.load(bof_pkl)
    entries = pickle.load(inv_pkl)

    k = idf.shape[0]
    img = cv2.imread(os.path.join(current_app.config['DATA_DIR'], uri))
    # 计算要搜索的图像的所有descriptor
    kp, des = RootSIFT().extract(img)
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
    scores = np.zeros([len(uris)])
    for bq, lq in zip(binary, label):
        for img_id, bt in entries[lq]['img_ids']:
            if he.ham_dist(bq, bt) < threshold:
                scores[img_id] += idf[lq]
    scores = scores / lens

    rank = np.argsort(-scores)
    print([round(scores[r], 4) for r in rank[:10]])
    images = [uris[r] for r in rank[:top_k]]
    return images
