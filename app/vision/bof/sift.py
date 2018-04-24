# -*- coding: utf-8 -*-

import cv2
from flask import current_app


def extract(image):
    sift = cv2.xfeatures2d.SIFT_create()
    return sift.detectAndCompute(image, None)
