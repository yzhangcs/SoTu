# -*- coding: utf-8 -*-

import cv2
import numpy as np


def consistency(pt_q, pt_t):
    src_pts = np.float32(pt_q).reshape(-1, 1, 2)
    dst_pts = np.float32(pt_t).reshape(-1, 1, 2)
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 3)
    inliers = np.sum(mask.ravel())
    return inliers
