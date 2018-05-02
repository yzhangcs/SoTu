

# -*- coding: utf-8 -*-

import os
import PIL
from utils import download, list_files


def get_oxbuild(root):
    url = 'http://www.robots.ox.ac.uk/~vgg/data/oxbuildings/oxbuild_images.tgz'
    filename = 'oxbuild_images.tgz'
    oxbuild_dir = 'oxbuild_images'

    cwd = os.getcwd()
    os.chdir(root)
    if not os.path.exists(oxbuild_dir):
        download(url, root, filename, untar=True)
    uris = list_files(oxbuild_dir, ('png', 'jpg', 'jpeg', 'gif'))
    os.chdir(cwd)
    return len(uris), uris
