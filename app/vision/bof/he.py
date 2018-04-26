# -*- coding: utf-8 -*-

import numpy as np


def get_medians(prj_all, label_all, k):
    sums = np.zeros([k, prj_all.shape[1]])
    freqs = [0] * k
    for prj, label in zip(prj_all, label_all):
        sums[label] += prj
        freqs[label] += 1
    medians = [s / f for s, f in zip(sums, freqs)]
    return medians


def bitspack(binary):
    result = np.int64()
    for b in binary:
        result = (result << 1) + b
    return result


def ham_dist(a, b):
    return bin(a ^ b).count("1")
