# -*- coding: utf-8 -*-

import cv2
import numpy as np


class RootSIFT:
    def __init__(self):
        self.extractor = cv2.xfeatures2d.SIFT_create()

    def extract(self, image, eps=1e-7):
        # 计算图片的所有keypoint和对应的descriptor
        kp, des = self.extractor.detectAndCompute(image, None)

        if len(kp) > 0:
            # 对所有descriptor进行L1归一化并取平方根，eps防止除数为0
            des /= (des.sum(axis=1, keepdims=True) + eps)
            des = np.sqrt(des)
        return kp, des

    def match(self, img1, img2):
        pass
