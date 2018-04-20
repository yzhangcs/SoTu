# -*- coding: utf-8 -*-

import os

import cv2
import numpy as np
from PIL import Image
from pylab import *
from scipy.cluster.vq import *
from sklearn import preprocessing
from sklearn.externals import joblib

import imutils


def search(uri):
    im_features, image_paths, idf, numWords, voc = joblib.load("bof.pkl")

    sift = cv2.xfeatures2d.SIFT_create()
    # 计算要搜索的图像的keypoint和对应的descriptor
    kp, des = sift.detectAndCompute(cv2.imread(uri), None)

    test_features = np.zeros((1, numWords), "float32")
    words, distance = vq(descriptors, voc)
    for w in words:
        test_features[0][w] += 1

    # Perform Tf-Idf vectorization and L2 normalization
    test_features = test_features*idf
    test_features = preprocessing.normalize(test_features, norm='l2')

    score = np.dot(test_features, im_features.T)
    rank_ID = np.argsort(-score)

    # Visualize the results
    figure()
    gray()
    subplot(5, 4, 1)
    imshow(im[:, :, ::-1])
    axis('off')
    for i, ID in enumerate(rank_ID[0][0:16]):
        img = Image.open(image_paths[ID])
        gray()
        subplot(5, 4, i+5)
        imshow(img)
        axis('off')

    show()
