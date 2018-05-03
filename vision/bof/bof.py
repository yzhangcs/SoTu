# -*- coding: utf-8 -*-

import os
import pickle

import click
import cv2
import numpy as np
from flask.cli import with_appcontext
from sklearn.cluster import MiniBatchKMeans

from . import ukbench
from .geo import consistency
from .he import HE
from .inv import InvFile
from .sift import SIFT


class BoF(object):
    def __init__(self):
        self.n, self.uris = ukbench.get_ukbench('data')
        self.k = 2000
        self.path = 'data/features/bof.pkl'
        self.sift = SIFT()
        self.he = HE(128, 64, self.k)
        self.inv = InvFile(self.k, self.n)

    def init_app(self, app):
        @click.command('extract')
        @with_appcontext
        def extract():
            self.extract()
        app.cli.add_command(extract)

    def extract(self):
        images = [cv2.imread(uri) for uri in self.uris]

        print("Get sift features of %d images" % self.n)
        # # 获取每幅图的所有关键点和对应的描述子
        # keypoints, descriptors = zip(
        #     *[self.sift.extract(img) for img in images]
        # )
        # # 每个sift特征转为rootsift
        # descriptors = [self.sift.rootsift(des) for des in descriptors]
        # self.sift.dump(keypoints, descriptors)
        keypoints, descriptors = self.sift.load()

        # 垂直堆叠所有的描述子，每个128维
        des_all = np.vstack([des for des in descriptors if des is not None])

        print("Start kmeans with %d centroids" % self.k)
        kmeans = MiniBatchKMeans(
            n_clusters=self.k, init_size=self.k * 3
        ).fit(des_all)
        # 映射每幅图的所有描述子到距其最近的聚类并得到聚类索引
        labels = [kmeans.predict(des) for des in descriptors]

        print("Porject %d descriptors from 128d to 64d" % len(des_all))
        projections = [self.he.project(des) for des in descriptors]
        prj_all = np.vstack([prj for prj in projections if prj is not None])
        label_all = np.hstack([label for label in labels if label is not None])

        print("Calculate medians of %d visual words" % self.k)
        self.he.fit(prj_all, label_all)

        print("Calculate binary signatures of %d projections" % len(des_all))
        # 得到每幅图所有描述子对应的Hamming编码
        signatures = [
            [self.he.signature(p, l) for p, l in zip(prj, label)]
            for prj, label in zip(projections, labels)
        ]

        # 建立聚类的倒排索引
        self.inv.dump(keypoints, signatures, labels)

        # 统计每幅图所有描述子所属聚类的频率向量
        freqs = np.array([
            np.bincount(label, minlength=self.k) for label in labels
        ])
        # 计算聚类频率矩阵的idf(sklearn的实现方式)
        idf = np.log((self.n + 1) / (np.sum((freqs > 0), axis=0) + 1)) + 1
        self.dump(kmeans, idf)

    def match(self, uri, top_k=20, reranking=1):
        kmeans, idf = self.load()
        entries = self.inv.load()
        # 计算描述子
        kp, des = self.sift.extract(cv2.imread(uri))
        # 计算每个关键点对应的关于角度和尺度的几何信息
        geom = [(k.pt, np.radians(k.angle), np.log2(k.octave)) for k in kp]
        # 映射所有描述子到距其最近的聚类并得到该聚类的索引
        label = kmeans.predict(des)

        # 根据投影矩阵对描述子降维
        prj = self.he.project(des)
        # 计算所有描述子对应的Hamming编码
        signature = [self.he.signature(p, l) for p, l in zip(prj, label)]

        # 定义hamming阈值
        threshold = 25
        print("Start to score all iamges")
        matches = [[] for i in range(self.n)]
        weights = [[] for i in range(self.n)]
        angle_diffs = [[] for i in range(self.n)]
        scale_diffs = [[] for i in range(self.n)]
        # 匹配所有所属聚类相同且对应编码的hamming距离不超过阈值的特征
        for sig_q, lbl_q, (pt_q, ang_q, sca_q) in zip(signature, label, geom):
            for img_id, features in entries[lbl_q].items():
                for pt_t, ang_t, sca_t, sig_t in features:
                    if self.he.distance(sig_q, sig_t) < threshold:
                        matches[img_id].append((pt_q, pt_t))
                        weights[img_id].append(idf[lbl_q])
                        angle_diffs[img_id].append(
                            np.arctan2(np.sin(ang_q - ang_t),
                                       np.cos(ang_q - ang_t))
                        )
                        scale_diffs[img_id].append(sca_q - sca_t)
        angle_scores = [
            max(np.histogram(ad, bins=8, range=(-np.pi, np.pi), weights=w)[0])
            for ad, w in zip(angle_diffs, weights)
        ]
        scale_scores = [
            max(np.histogram(sd, bins=8, range=(-5, 5), weights=w)[0])
            for sd, w in zip(scale_diffs, weights)
        ]
        scores = np.array([min(a, s)
                           for a, s in zip(angle_scores, scale_scores)
                           ])
        rank = np.argsort(-scores)[:top_k]

        print("Rerank the existing results %d times" % reranking)
        for i in range(reranking):
            inliers = np.zeros(top_k)
            for i, r in enumerate(rank):
                pt_q, pt_t = zip(*matches[r])
                inliers[i] = consistency(pt_q, pt_t)
            rank = [r for s, r in sorted(zip(-inliers, rank))]
        ukbench.evaluate(uri, rank)
        images = [self.uris[r] for r in rank]
        return images

    def dump(self, kmeans, idf):
        with open(self.path, 'wb') as bof_pkl:
            pickle.dump((kmeans, idf), bof_pkl)

    def load(self):
        with open(self.path, 'rb') as bof_pkl:
            kmeans, idf = pickle.load(bof_pkl)
        return kmeans, idf
