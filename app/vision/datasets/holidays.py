

# -*- coding: utf-8 -*-

import os
import PIL
from app.utils import download, list_files


def get_holidays(root):
    url = 'ftp://ftp.inrialpes.fr/pub/lear/douze/data/jpg1.tar.gz'
    filename = 'jpg1.tar.gz'
    holidays_dir = 'jpg'

    cwd = os.getcwd()
    os.chdir(root)
    if not os.path.exists(holidays_dir):
        download(url, root, filename, untar=True)
    uris = list_files(holidays_dir, ('png', 'jpg', 'jpeg', 'gif'))
    os.chdir(cwd)
    return uris
