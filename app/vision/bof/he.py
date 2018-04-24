# -*- coding: utf-8 -*-

import numpy as np
from scipy.spatial.distance import hamming


def get_proj_matrix(db, d):
    # 生成d * d的符合标准正态分布的随机矩阵
    M = np.random.randn(d, d)
    # QR分解得到正交矩阵Q
    Q, R = np.linalg.qr(M)
    return Q[:d_b, :]


def get_medians(projections, labels, k):
    sum = np.zeros(k, projections.shape[1])
    freq = [0] * k
    for proj, lbl in zip(projections, labels):
        sum[lbl][0] += proj
        freq[lbl] += 1
    medians = [s / freq[i] for i, s in enumerate(sum)]
    return medians


def get_binary(prj, lbl, medians):
    return [p > medians[lbl[i]] for i, p in enumerate(prj)]


def get_score(bin1, bin2, threshold, idx1, idx2, idf):
    scores = 0
    num_bin1 = np.array(bin1).shape[0]
    num_bin2 = np.array(bin2).shape[0]
    for i in range(bin1):
        for j in range(bin2):
            if (hamming(bin1[i], bin2[j]) < threshold):
                scores += (idx1 == idx2) * idf[idx1]
    return get_score
