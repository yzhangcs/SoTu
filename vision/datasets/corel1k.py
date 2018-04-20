

# -*- coding: utf-8 -*-

import os
import PIL
from utils import download, list_files


def get_corel1k(root):
    url = 'http://wang.ist.psu.edu/~jwang/test1.tar'
    filename = 'test1.tar'
    caltech101_dir = 'image.orig'

    cwd = os.getcwd()
    os.chdir(root)
    if not os.path.exists(caltech101_dir):
        download(url, root, filename, untar=True)
    uris = list_files(caltech101_dir, ('png', 'jpg', 'jpeg', 'gif'))
    os.chdir(cwd)
    return uris
