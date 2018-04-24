# -*- coding: utf-8 -*-

import cv2
from flask import current_app


def extract(images):
    sift = cv2.xfeatures2d.SIFT_create()
    kp_all, des_all = zip(
        *[sift.detectAndCompute(img, None) for img in images]
    )
    return kp_all, des_all
