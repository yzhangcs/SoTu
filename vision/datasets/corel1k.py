

# -*- coding: utf-8 -*-

import posixpath

from utils import download, list_files


def get_corel1k(root):
    url = 'http://wang.ist.psu.edu/~jwang/test1.tar'
    filename = 'test1.tar'
    corel1k_dir = 'image.orig'

    if not posixpath.exists(posixpath.join(root, corel1k_dir)):
        download(url, root, filename, untar=True)
    uris = list_files(posixpath.join(root, corel1k_dir),
                      ('png', 'jpg', 'jpeg', 'gif'))
    return len(uris), uris
