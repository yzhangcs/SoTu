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

    def score(self, feature_q, feature_t):
        kp_q, des_q = feature_q
        kp_t, des_t = feature_t

        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        ratio = 0.7  # as per Lowe's test

        flann = cv2.FlannBasedMatcher(index_params, search_params)
        # 对des_q中的每个描述子，在des_t中找到最好的两个匹配
        two_nn = flann.knnMatch(des_q, des_t, k=2)
        # 保存所有显著好于次匹配的最好匹配
        one_nn = [first for first, second in two_nn
                  if first.distance < ratio * second.distance]
        if len(one_nn) > 0:
            pts_q = np.float32(
                [kp_q[m.queryIdx].pt for m in one_nn]
            ).reshape(-1, 1, 2)
            pts_t = np.float32(
                [kp_t[m.trainIdx].pt for m in one_nn]
            ).reshape(-1, 1, 2)
            M, mask = cv2.findHomography(pts_q, pts_t, cv2.RANSAC, 5)
            return np.sum(mask.ravel())
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
