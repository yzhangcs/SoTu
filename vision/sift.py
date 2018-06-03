# -*- coding: utf-8 -*-

import os
import pickle

import numpy as np

import cv2


class SIFT(object):
    def __init__(self, root):
        self.path = os.path.join(root, 'sift')
        self.extractor = cv2.xfeatures2d.SIFT_create()

    def extract(self, gray, rootsift=True):
        # 计算图片的所有关键点和对应的描述子
        kp, des = self.extractor.detectAndCompute(gray, None)
        if rootsift:
            des = self.rootsift(des)
        return kp, des

    def match(self, des_q, des_t):
        ratio = 0.7  # 按照Lowe的测试
        flann = cv2.FlannBasedMatcher()
        # 对des_q中的每个描述子，在des_t中找到最好的两个匹配
        two_nn = flann.knnMatch(des_q, des_t, k=2)
        # 找到所有显著好于次匹配的最好匹配，得到对应的索引对
        matches = [(first.queryIdx, first.trainIdx) for first, second in two_nn
                   if first.distance < ratio * second.distance]
        return matches

    def filter(self, pt_qt):
        if len(pt_qt) > 0:
            pt_q, pt_t = zip(*pt_qt)
            # 获取匹配坐标的变换矩阵和正常点的掩码
            M, mask = cv2.findHomography(np.float32(pt_q).reshape(-1, 1, 2),
                                         np.float32(pt_t).reshape(-1, 1, 2),
                                         cv2.RANSAC, 3)
            return mask.ravel().tolist()
        else:
            return []

    def draw(self, img_q, img_t, pt_qt):
        import matplotlib
        matplotlib.use('Agg')
        from matplotlib import pyplot as plt
        from matplotlib.patches import ConnectionPatch

        fig, (ax_q, ax_t) = plt.subplots(1, 2, figsize=(8, 4))
        for pt_q, pt_t in pt_qt:
            con = ConnectionPatch(pt_t, pt_q,
                                  coordsA='data', coordsB='data',
                                  axesA=ax_t, axesB=ax_q,
                                  color='g', linewidth=0.5)
            ax_t.add_artist(con)
            ax_q.plot(pt_q[0], pt_q[1], 'rx')
            ax_t.plot(pt_t[0], pt_t[1], 'rx')
        ax_q.imshow(img_q)
        ax_t.imshow(img_t)
        ax_q.axis('off')
        ax_t.axis('off')
        plt.subplots_adjust(wspace=0, hspace=0)
        plt.show()

    @classmethod
    def rootsift(cls, des, eps=1e-7):
        if des is not None:
            # 对所有描述子进行L1归一化并取平方根，eps防止除数为0
            des /= (des.sum(axis=1, keepdims=True) + eps)
            des = np.sqrt(des)
        return des

    def dump(self, kp, des, filename):
        tmp = [
            (kp.pt, kp.size, kp.angle, kp.response, kp.octave, kp.class_id)
            for kp in kp
        ]
        with open(os.path.join(self.path, filename), 'wb') as sift_pkl:
            pickle.dump((tmp, des), sift_pkl)

    def load(self, filename):
        with open(os.path.join(self.path, filename), 'rb') as sift_pkl:
            tmp, des = pickle.load(sift_pkl)
            kp = [
                cv2.KeyPoint(x=t[0][0], y=t[0][1], _size=t[1], _angle=t[2],
                             _response=t[3], _octave=t[4], _class_id=t[5])
                for t in tmp
            ]
        return kp, des
