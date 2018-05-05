# -*- coding: utf-8 -*-

import pickle

import cv2
import numpy as np


class SIFT(object):
    def __init__(self):
        self.path = 'data/features/sift.pkl'
        self.extractor = cv2.xfeatures2d.SIFT_create()

    def extract(self, image, rootsift=True):
        # 计算图片的所有关键点和对应的描述子
        kp, des = self.extractor.detectAndCompute(image, None)
        if rootsift:
            des = self.rootsift(des)
        return kp, des

    def match(self, des_q, des_t):
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        ratio = 0.7  # 按照Lowe的测试

        flann = cv2.FlannBasedMatcher(index_params, search_params)
        # 对des_q中的每个描述子，在des_t中找到最好的两个匹配
        two_nn = flann.knnMatch(des_q, des_t, k=2)
        # 找到所有显著好于次匹配的最好匹配，得到对应的索引对
        pairs = [(first.queryIdx, first.trainIdx) for first, second in two_nn
                 if first.distance < ratio * second.distance]
        return pairs

    def score(self, pt_q, pt_t):
        if len(pt_q) > 0:
            # 获取匹配坐标的变换矩阵和正常点的掩码
            M, mask = cv2.findHomography(np.float32(pt_q).reshape(-1, 1, 2),
                                         np.float32(pt_t).reshape(-1, 1, 2),
                                         cv2.RANSAC, 5)
            return np.sum(mask)
        else:
            return 0

    @classmethod
    def rootsift(cls, des, eps=1e-7):
        if des is not None:
            # 对所有描述子进行L1归一化并取平方根，eps防止除数为0
            des /= (des.sum(axis=1, keepdims=True) + eps)
            des = np.sqrt(des)
        return des

    def load(self):
        with open(self.path, 'rb') as sift_pkl:
            tmps, descriptors = pickle.load(sift_pkl)
            keypoints = [
                [cv2.KeyPoint(x=t[0][0], y=t[0][1], _size=t[1], _angle=t[2],
                              _response=t[3], _octave=t[4], _class_id=t[5])
                    for t in tmp] for tmp in tmps
            ]
        return keypoints, descriptors

    def dump(self, keypoints, descriptors):
        tmps = [
            [(k.pt, k.size, k.angle, k.response, k.octave, k.class_id)
             for k in kp] for kp in keypoints
        ]
        with open(self.path, 'wb') as sift_pkl:
            pickle.dump((tmps, descriptors), sift_pkl)
