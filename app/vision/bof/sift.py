# -*- coding: utf-8 -*-

import os
import pickle

import cv2
from flask import current_app


def extract(img):
    sift = cv2.xfeatures2d.SIFT_create()
    return sift.detectAndCompute(img, kp)


def extract_all(images):
    sift_path = os.path.join(current_app.config['FEATURE_DIR'], 'sift.pkl')
    if os.path.exists(sift_path):
        with open(sift_path, 'rb') as s:
            keypoints, descriptors = pickle.load(s)
    else:
        sift = cv2.xfeatures2d.SIFT_create()
        keypoints, descriptors = [], []
        for img in images:
            kp = sift.detect(img, None)
            if len(kp) > 0:
                kp, des = sift.compute(img, kp)
                keypoints.append(kp)
                descriptors.append(des)
        with open(sift_path, 'wb') as s:
            pickle.dump((keypoints, descriptors), s)
    return keypoints, descriptors
