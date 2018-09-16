# -*- coding: utf-8 -*-

import pickle

import numpy as np


class INV(object):
    def __init__(self, k, n):
        self.k = k
        self.n = n

    def dump(self, keypoints, signatures, labels, path):
        entries = [[] for i in range(self.k)]
        # 添加每幅图的所有关键点的角度、尺度信息及对应的Hamming编码到倒排索引中
        for i in range(self.n):
            for k, s, l in zip(keypoints[i], signatures[i], labels[i]):
                entries[l].append(
                    (i, np.radians(k.angle), np.log2(k.size), s)
                )
        with open(path, 'wb') as inv_pkl:
            pickle.dump(entries, inv_pkl)

    def load(self, path):
        with open(path, 'rb') as inv_pkl:
            entries = pickle.load(inv_pkl)
        return entries
