

# -*- coding: utf-8 -*-

import os
import PIL
from app.utils import download, list_files


def get_corel1k(root):
    url = 'http://wang.ist.psu.edu/~jwang/test1.tar'
    filename = 'test1.tar'
    corel1k_dir = 'image.orig'

    cwd = os.getcwd()
    os.chdir(root)
    if not os.path.exists(corel1k_dir):
        download(url, root, filename, untar=True)
    uris = list_files(corel1k_dir, ('png', 'jpg', 'jpeg', 'gif'))
    os.chdir(cwd)
    return uris
