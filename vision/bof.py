# -*- coding: utf-8 -*-

import pickle
import time

import click
import cv2
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from werkzeug.utils import cached_property

from .he import HE
from .inv import INV
from .sift import SIFT
from .ukbench import UKBENCH
from .wgc import WGC


class BoF(object):
    def __init__(self):
        self.k = 5000
        self.bof_path = 'data/bof.pkl'
        self.inv_path = 'data/inv.pkl'
        self.ukbench = UKBENCH('data')
        self.n = len(self.ukbench)
        self.sift = SIFT('data')
        self.inv = INV(self.k, self.n)

    def init_app(self, app):
        @click.command('extract')
        def extract():
            self.extract()

        @click.command('evaluate')
        def evaluate():
            queries = []
            for i in range(0, self.n, 4):
                start = time.time()
                matches = self.match(self.ukbench[i])
                ap = self.ukbench.evaluate(self.ukbench[i], matches)
                elapse = time.time() - start
                print("Query %s: ap = %4f, %4fs elapsed" %
                      (self.ukbench[i], ap, elapse))
                queries.append((ap, elapse))
            mAP, mT = np.mean(queries, axis=0)
            print("mAP of the %d images is %4f, %4fs per query" %
                  (len(queries), mAP, mT))

        app.cli.add_command(extract)
        app.cli.add_command(evaluate)

    def extract(self):
        print("Get sift features of %d images" % self.n)
        # 获取每幅图的所有关键点和对应的描述子
        keypoints, descriptors = zip(*[
            self.sift.extract(cv2.imread(uri, cv2.IMREAD_GRAYSCALE),
                              rootsift=True)
            for uri in self.ukbench
        ])
        for i, (kp, des) in enumerate(zip(keypoints, descriptors)):
            self.sift.dump(kp, des, str(i))
        # keypoints, descriptors = zip(
        #     *[self.sift.load(str(i)) for i in range(self.n)]
        # )
        # 垂直堆叠所有的描述子，每个128维
        des_all = np.vstack([des for des in descriptors])

        print("Start kmeans with %d clusters" % self.k)
        kmeans = MiniBatchKMeans(
            n_clusters=self.k,
            batch_size=1000,
            random_state=0,
            init_size=self.k * 3
        ).fit(des_all)
        # 映射每幅图的所有描述子到距其最近的聚类并得到聚类索引
        labels = [kmeans.predict(des) for des in descriptors]

        print("Porject %d descriptors from 128d to 64d" % len(des_all))
        he = HE(64, 128, self.k)
        projections = [he.project(des) for des in descriptors]
        prj_all = np.vstack([prj for prj in projections])
        label_all = np.hstack([label for label in labels])

        print("Calculate medians of %d visual words" % self.k)
        he.fit(prj_all, label_all)

        print("Calculate binary signatures of %d projections" % len(des_all))
        signatures = [
            [he.signature(p, l) for p, l in zip(prj, label)]
            for prj, label in zip(projections, labels)
        ]

        # 建立聚类的倒排索引
        self.inv.dump(keypoints, signatures, labels, self.inv_path)

        # 统计每幅图所有描述子所属聚类的频率向量
        freqs = np.array([
            np.bincount(label, minlength=self.k) for label in labels
        ])
        # 计算每幅图频率向量的模
        norms = np.array([np.linalg.norm(freq) for freq in freqs])
        # 计算聚类频率矩阵的idf(sklearn的实现方式)
        idf = np.log((self.n + 1) / (np.sum((freqs > 0), axis=0) + 1)) + 1

        with open(self.bof_path, 'wb') as bof_pkl:
            pickle.dump((kmeans, he, norms, idf), bof_pkl)

    def match(self, uri, top_k=20, ht=23, rerank=True):
        kmeans, he, norms, idf = self.bof
        # 计算关键点和描述子
        kp, des = self.sift.extract(cv2.imread(uri, cv2.IMREAD_GRAYSCALE),
                                    rootsift=True)
        # 计算每个关键点对应的关于角度和尺度的几何信息
        geo = [(np.radians(k.angle), np.log2(k.size)) for k in kp]
        # 映射所有描述子到距其最近的聚类并得到该聚类的索引
        label = kmeans.predict(des)

        # 根据投影矩阵对描述子降维
        prj = he.project(des)
        # 计算所有描述子对应的Hamming编码
        signature = [he.signature(p, l) for p, l in zip(prj, label)]

        # wgc = WGC(self.n, 17, 7)
        scores = np.zeros(self.n)
        # 匹配所有所属聚类相同且对应编码的hamming距离不超过阈值的特征
        for (ang_q, sca_q), sig_q, lbl_q in zip(geo, signature, label):
            for img_id, ang_t, sca_t, sig_t in self.entries[lbl_q]:
                if he.distance(sig_q, sig_t) < ht:
                    scores[img_id] += idf[lbl_q]
                    # wgc.vote(img_id,
                    #          np.arctan2(np.sin(ang_t - ang_q),
                    #                     np.cos(ang_t - ang_q)),
                    #          sca_t - sca_q)
        # scores *= wgc.filter()
        scores = scores / norms
        rank = np.argsort(-scores)[:top_k]

        if rerank:
            scores = np.zeros(top_k)
            keypoints, descriptors = zip(
                *[self.sift.load(str(r)) for r in rank]
            )
            # 使用kNN算法获取匹配坐标
            pairs = [
                [(kp[q].pt, keypoints[i][t].pt)
                 for q, t in self.sift.match(des, descriptors[i])]
                for i in range(top_k)
            ]
            for i in range(top_k):
                mask = self.sift.filter(pairs[i])
                scores[i] += np.sum(mask)
            rank = [r for s, r in sorted(zip(-scores, rank))]
        images = [self.ukbench[r] for r in rank]
        return images

    @cached_property
    def bof(self):
        with open(self.bof_path, 'rb') as bof_pkl:
            kmeans, he, norms, idf = pickle.load(bof_pkl)
        return kmeans, he, norms, idf

    @cached_property
    def entries(self):
        return self.inv.load(self.inv_path)
