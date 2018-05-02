# -*- coding: utf-8 -*-

import os
import PIL
from utils import download, list_files


def get_caltech256(root):
    url = 'http://www.vision.caltech.edu/Image_Datasets/Caltech256/256_ObjectCategories.tar'
    filename = '256_ObjectCategories.tar'
    caltech256_dir = '256_ObjectCategories'

    cwd = os.getcwd()
    os.chdir(root)
    if not os.path.exists(caltech256_dir):
        download(url, root, filename, untar=True)
    uris = list_files(caltech256_dir, ('png', 'jpg', 'jpeg', 'gif'))
    os.chdir(cwd)
    return len(uris), uris
