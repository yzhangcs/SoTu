# -*- coding: utf-8 -*-

import pickle

import cv2
import numpy as np


class SIFT(object):
    def __init__(self):
        self.path = 'data/features/sift.pkl'
        self.extractor = cv2.xfeatures2d.SIFT_create()

    def extract(self, image):
        # 计算图片的所有关键点和对应的描述子
        kp, des = self.extractor.detectAndCompute(image, None)
        return kp, des

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
                [cv2.KeyPoint(x=t[0][0], y=t[0][1], _size=t[1],
                              _angle=t[2], _response=t[3],
                              _octave=t[4], _class_id=t[5])
                 for t in tmp]
                for tmp in tmps
            ]
        return keypoints, descriptors

    def dump(self, keypoints, descriptors):
        tmps = [
            [(k.pt, k.size, k.angle, k.response,
              k.octave, k.class_id) for k in kp]
            for kp in keypoints
        ]
        with open(self.path, 'wb') as sift_pkl:
            pickle.dump((tmps, descriptors), sift_pkl)
