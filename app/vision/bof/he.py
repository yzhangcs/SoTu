# -*- coding: utf-8 -*-

import numpy as np


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


def ham_dist(vec_a, vec_b):
    return sum(np.logical_xor(vec_a, vec_b))


def get_score(bin_test, bin_train, threshold, lbl_test, lbl_train, idf):
    num_test = len(lbl_test)
    num_train = len(lbl_train)
    score = np.zeros([num_test, num_train])

    for i in range(num_test):
        for j in range(num_train):
            if lbl_test[i] == lbl_train[j]:
                if ham_dist(bin_test[i], bin_train[j]) < threshold:
                    score[i][j] = 1
    weighted = sum([idf[l] * sum(s) for l, s in zip(lbl_test, score)])
    return weighted / (num_test * num_train)
