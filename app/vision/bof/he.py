# -*- coding: utf-8 -*-

import numpy as np
from scipy.spatial.distance import hamming


def get_proj_matrix(db, d):
    # 生成d * d的符合标准正态分布的随机矩阵
    M = np.random.randn(d, d)
    # QR分解得到正交矩阵Q
    Q, R = np.linalg.qr(M)
    return Q[:db, :]


def get_medians(prj_all, lbl_all, k):
    sums = np.zeros([k, prj_all.shape[1]])
    freqs = [0] * k
    for prj, lbl in zip(prj_all, lbl_all):
        sums[lbl] += prj
        freqs[lbl] += 1
    medians = [s / f for s, f in zip(sums, freqs)]
    return medians


def get_binary(prj, lbl, medians):
    return [p > medians[i] for p, i in zip(prj, lbl)]


def get_score(bin_test, bin_train, threshold, lbl_test, lbl_train, idf):
    score = 0
    num_test = len(bin_test)
    num_train = len(bin_train)
    for i in range(num_test):
        for j in range(num_train):
            if (hamming(bin_test[i], bin_train[j]) < threshold):
                score += (lbl_test[i] == lbl_train[j]) * idf[lbl_test[i]]
    score /= (num_test * num_train)
    return score
