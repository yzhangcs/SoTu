# -*- coding: utf-8 -*-

import os
import pickle
import time

import click
import cv2
import numpy as np
from flask.cli import with_appcontext
from sklearn.cluster import MiniBatchKMeans

from . import ukbench
from .he import HE
from .inv import InvFile
from .sift import SIFT


class BoF(object):
    def __init__(self):
        self.k = 5000
        self.n, self.uris = ukbench.get_ukbench('data')
        self.path = 'data/features/bof.pkl'
        self.sift = SIFT()
        self.inv = InvFile(self.k, self.n)

    def init_app(self, app):
        @click.command('extract')
        def extract():
            self.extract()

        @click.command('evaluate')
        def evaluate():
            aps = []
            for i in range(0, 500, 4):
                start = time.time()
                ap = ukbench.evaluate(self.uris[i], self.match(self.uris[i]))
                print('Query %s: ap = %4f, %4fs elapsed' %
                      (self.uris[i], ap, time.time() - start))
                aps.append(ap)
            print('mAP of the %d images is %4f' % (len(aps), np.mean(aps)))
        app.cli.add_command(extract)
        app.cli.add_command(evaluate)

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
            n_clusters=self.k, batch_size=1000, init_size=self.k * 3
        ).fit(des_all)
        # 映射每幅图的所有描述子到距其最近的聚类并得到聚类索引
        labels = [kmeans.predict(des) for des in descriptors]

        print("Porject %d descriptors from 128d to 64d" % len(des_all))
        he = HE(64, 128, self.k)
        projections = [he.project(des) for des in descriptors]
        prj_all = np.vstack([prj for prj in projections if prj is not None])
        label_all = np.hstack([label for label in labels if label is not None])

        print("Calculate medians of %d visual words" % self.k)
        he.fit(prj_all, label_all)

        print("Calculate binary signatures of %d projections" % len(des_all))
        signatures = [
            [he.signature(p, l) for p, l in zip(prj, label)]
            for prj, label in zip(projections, labels)
        ]

        # 建立聚类的倒排索引
        self.inv.dump(keypoints, signatures, labels)

        # 统计每幅图所有描述子所属聚类的频率向量
        freqs = np.array([
            np.bincount(label, minlength=self.k) for label in labels
        ])
        # 计算每幅图频率向量的模
        norms = np.array([np.linalg.norm(freq) for freq in freqs])
        # 计算聚类频率矩阵的idf(sklearn的实现方式)
        idf = np.log((self.n + 1) / (np.sum((freqs > 0), axis=0) + 1)) + 1
        self.dump(kmeans, he, norms, idf)

    def match(self, uri, top_k=20, rerank=True):
        kmeans, he, norms, idf = self.load()
        entries = self.inv.load()
        # 计算描述子
        kp, des = self.sift.extract(cv2.imread(uri))
        # 计算每个关键点对应的关于角度和尺度的几何信息
        geo = [(k.pt, np.radians(k.angle), np.log2(k.octave)) for k in kp]
        # 映射所有描述子到距其最近的聚类并得到该聚类的索引
        label = kmeans.predict(des)

        # 根据投影矩阵对描述子降维
        prj = he.project(des)
        # 计算所有描述子对应的Hamming编码
        signature = [he.signature(p, l) for p, l in zip(prj, label)]

        # 定义hamming阈值
        threshold = 24
        matches = [[] for i in range(self.n)]
        weights = [[] for i in range(self.n)]
        angle_diffs = [[] for i in range(self.n)]
        scale_diffs = [[] for i in range(self.n)]
        # 匹配所有所属聚类相同且对应编码的hamming距离不超过阈值的特征
        for sig_q, lbl_q, (pt_q, ang_q, sca_q) in zip(signature, label, geo):
            for img_id, pt_t, ang_t, sca_t, sig_t in entries[lbl_q]:
                if he.distance(sig_q, sig_t) < threshold:
                    matches[img_id].append((pt_q, pt_t))
                    weights[img_id].append(idf[lbl_q])
                    angle_diffs[img_id].append(
                        np.arctan2(np.sin(ang_q - ang_t),
                                   np.cos(ang_q - ang_t))
                    )
                    scale_diffs[img_id].append(sca_q - sca_t)
        angle_scores = [
            max(np.histogram(ad, bins=127,
                             range=(-np.pi, np.pi), weights=w)[0])
            for ad, w in zip(angle_diffs, weights)
        ]
        scale_scores = [
            max(np.histogram(sd, bins=127, range=(-5, 5), weights=w)[0])
            for sd, w in zip(scale_diffs, weights)
        ]
        scores = np.array(
            [min(a, s) for a, s in zip(angle_scores, scale_scores)]
        )
        scores = scores / norms
        rank = np.argsort(-scores)[:top_k]

        if rerank:
            scores = np.zeros(top_k)
            # keypoints, descriptors = self.sift.load()
            for i, r in enumerate(rank):
                pt_q, pt_t = [], []
                # # 使用kNN算法获取匹配坐标
                # pairs = self.sift.match(des, descriptors[r])
                # for index_q, index_t in pairs:
                #     pt_q.append(kp[index_q].pt)
                #     pt_t.append(keypoints[r][index_t].pt)
                for q, t in matches[r]:
                    pt_q.append(q)
                    pt_t.append(t)
                scores[i] = self.sift.score(pt_q, pt_t)
            rank = [r for s, r in sorted(zip(-scores, rank))]
        images = [self.uris[r] for r in rank]
        return images

    def dump(self, kmeans, he, norms, idf):
        with open(self.path, 'wb') as bof_pkl:
            pickle.dump((kmeans, he, norms, idf), bof_pkl)

    def load(self):
        with open(self.path, 'rb') as bof_pkl:
            kmeans, he, norms, idf = pickle.load(bof_pkl)
        return kmeans, he, norms, idf
