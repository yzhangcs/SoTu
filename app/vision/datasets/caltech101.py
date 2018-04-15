# -*- coding: utf-8 -*-

import os
import PIL
from app.utils import download, list_files


def get_caltech101(root):
    url = 'http://www.vision.caltech.edu/Image_Datasets/Caltech101/101_ObjectCategories.tar.gz'
    filepath = os.path.join(root, '101_ObjectCategories.tar.gz')
    caltech101_path = os.path.join(root, '101_ObjectCategories')
    if not os.path.exists(caltech101_path):
        download(url, filepath, True)
    return list_files(caltech101_path, ('png', 'jpg', 'jpeg', 'gif'))
