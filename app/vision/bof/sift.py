# -*- coding: utf-8 -*-

import cv2
from flask import current_app


def extract(images):
    sift = cv2.xfeatures2d.SIFT_create()
    keypoints, descriptors = zip(
        *[sift.detectAndCompute(img, None) for img in images]
    )
    return keypoints, descriptors
