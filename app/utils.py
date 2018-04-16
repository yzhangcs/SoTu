# -*- coding: utf-8 -*-

import os
import tarfile
from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve


def download(url, path, untar=False):
    if os.path.exists(path):
        print('Data already downloaded')
    else:
        print('Downloading data from %s' % url)
        err_msg = 'URL fetch failure on {}: {} -- {}'
        try:
            try:
                urlretrieve(url, path)
            except URLError as e:
                raise Exception(err_msg.format(url, e.errno, e.reason))
            except HTTPError as e:
                raise Exception(err_msg.format(url, e.code, e.msg))
        except (Exception, KeyboardInterrupt) as e:
            print(e)
            if os.path.exists(path):
                os.remove(path)
    if untar is True:
        with tarfile.open(path) as tar:
            tar.extractall(os.path.dirname(path))


def list_files(path, suffix):
    names = []
    for name in os.listdir(path):
        fd = os.path.join(path, name)
        if os.path.isfile(fd) and fd.endswith(suffix):
            names.append(fd)
        if os.path.isdir(fd):
            names.extend(list_files(fd, suffix))
    return names
