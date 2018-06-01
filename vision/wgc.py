# -*- coding: utf-8 -*-

import numpy as np


class WGC(object):
    def __init__(self, n, angle_bins, scale_bins):
        self.n = n
        self.angle_bins, self.scale_bins = angle_bins, scale_bins
        self.angle_hists = np.zeros((self.n, self.angle_bins))
        self.scale_hists = np.zeros((self.n, self.scale_bins))

    def vote(self, i, diff, scale_diff):
        angle_index = self.quantize_angle(diff)
        scale_index = self.quantize_scale(diff)
        if angle_index >= 0 and angle_index < self.angle_bins:
            self.angle_hists[i][angle_index] += 1
        if scale_index >= 0 and scale_index < self.scale_bins:
            self.scale_hists[i][scale_index] += 1

    def filter(self):
        am = np.max([self.movmean(h, 3) for h in self.angle_hists], axis=1)
        sm = np.max([self.movmean(h, 3) for h in self.scale_hists], axis=1)
        return np.min(np.vstack((am, sm)), axis=0)

    def quantize_angle(self, diff):
        return int((diff + np.pi) * self.angle_bins / (2 * np.pi))

    def quantize_scale(self, diff):
        return int((diff + 3) * self.scale_bins / 6)

    def movmean(self, hist, window):
        cumsum = np.cumsum(np.insert(hist, 0, 0))
        return (cumsum[window:] - cumsum[: -window]) / float(window)
