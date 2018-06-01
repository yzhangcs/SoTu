# -*- coding: utf-8 -*-

import numpy as np


class HE(object):
    def __init__(self, db, d, k):
        self.k = k
        # 生成(d, d)的符合标准正态分布的随机矩阵
        self.M = np.random.randn(d, d)
        # QR分解得到正交矩阵Q
        self.Q, R = np.linalg.qr(self.M)
        # 获取(d, db)的投影矩阵
        self.P = self.Q[:db, :]
        # 建立(k, db)的中值矩阵
        self.medians = np.zeros([self.k, db])

    def project(self, des):
        return np.dot(des, self.P.T)

    def fit(self, prj_all, label_all, eps=1e-7):
        # 统计所属聚类的频率，eps防止除数为0
        freqs = [eps] * self.k
        for prj, label in zip(prj_all, label_all):
            self.medians[label] += prj
            freqs[label] += 1
        self.medians = [m / f for m, f in zip(self.medians, freqs)]

    def signature(self, prj, label):
        signature = np.uint64()
        bins = prj > self.medians[label]
        # 压缩为64bits
        for i, b in enumerate(bins[::-1]):
            signature = np.bitwise_or(signature, np.uint64(2**i * b))
        return signature

    def distance(self, sig_q, sig_t):
        return bin(sig_q ^ sig_t).count("1")
