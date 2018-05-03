

# -*- coding: utf-8 -*-

import os
import posixpath
import re

from utils import download, list_files


def get_ukbench(root):
    url = 'https://ia800809.us.archive.org/5/items/ukbench/ukbench.zip'
    filename = 'ukbench.zip'
    ukbench_dir = 'ukbench'

    if not posixpath.exists(posixpath.join(root, ukbench_dir)):
        download(url, root, filename, untar=True)
    uris = list_files(posixpath.join(root, ukbench_dir, 'full'),
                      ('png', 'jpg', 'jpeg', 'gif'))
    return len(uris), uris


def evaluate(uri, images):
    def id_of(img):
        return int(re.split(r'(\d+)', os.path.basename(img))[1])
    img_id = id_of(uri)
    min_id = img_id - img_id % 4
    max_id = min_id + 4
    results = [id_of(img) for img in images]

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
