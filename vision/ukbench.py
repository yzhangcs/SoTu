# -*- coding: utf-8 -*-

import os
import posixpath
import re

from utils import download, list_files, unzip


class UKBENCH(object):
    url = 'https://archive.org/download/ukbench/ukbench.zip'
    filename = 'ukbench.zip'
    ukbench_dir = 'ukbench'

    def __init__(self, root):
        self.root = root
        if not posixpath.exists(posixpath.join(self.root, self.ukbench_dir)):
            download(self.root, self.filename, self.url)
            unzip(self.root, self.filename, self.ukbench_dir)
        self.uris = sorted(list_files(root=posixpath.join(self.root,
                                                          self.ukbench_dir,
                                                          'full'),
                                      suffix=('png', 'jpg', 'jpeg', 'gif')))

    def __getitem__(self, index):
        return self.uris[index]

    def __iter__(self):
        return iter(self.uris)

    def __len__(self):
        return len(self.uris)

    def evaluate(self, img_q, images):
        img_id = self.id_of(img_q)
        min_id = img_id - img_id % 4
        max_id = min_id + 4
        results = [self.id_of(img) for img in images]

        precision = [0] * len(results)
        recall = [0] * len(results)
        positives = 0
        ap = 0

        for i, result in enumerate(results):
            if result >= min_id and result < max_id:
                positives += 1
            precision[i] = positives / (i + 1)
            recall[i] = positives / 4

        pr_sum = precision[0]
        for i in range(1, len(precision)):
            if recall[i] > recall[i - 1]:
                pr_sum += precision[i]
        ap = pr_sum / 4
        return ap

    def id_of(self, uri):
        return int(re.split(r'(\d+)', os.path.basename(uri))[1])
