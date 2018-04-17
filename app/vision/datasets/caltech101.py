# -*- coding: utf-8 -*-

import os
import PIL
from app.utils import download, list_files


def get_caltech101(root):
    url = 'http://www.vision.caltech.edu/Image_Datasets/Caltech101/101_ObjectCategories.tar.gz'
    filename = '101_ObjectCategories.tar.gz'
    caltech101_dir = '101_ObjectCategories'

    cwd = os.getcwd()
    os.chdir(root)
    if not os.path.exists(caltech101_dir):
        download(url, root, filename, untar=True)
    images = list_files(caltech101_dir, ('png', 'jpg', 'jpeg', 'gif'))
    os.chdir(cwd)
    return images
