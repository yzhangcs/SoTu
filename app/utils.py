# -*- coding: utf-8 -*-

import os
import posixpath
import tarfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlretrieve


def download(url, root, filename, untar=False):
    fpath = os.path.join(root, filename)
    if not os.path.exists(root):
        os.mkdir(root)
    if os.path.exists(fpath):
        print('Data already downloaded')
    else:
        print('Downloading ' + url + ' to ' + fpath)
        err_msg = 'URL fetch failure on {}: {} -- {}'
        try:
            try:
                urlretrieve(url, fpath)
            except URLError as e:
                raise Exception(err_msg.format(url, e.errno, e.reason))
            except HTTPError as e:
                raise Exception(err_msg.format(url, e.code, e.msg))
        except (Exception, KeyboardInterrupt) as e:
            print(e)
            if os.path.exists(fpath):
                os.remove(fpath)
    if untar is True:
        with tarfile.open(fpath) as tar:
            tar.extractall(os.path.dirname(fpath))


def list_files(root, suffix):
    names = []
    for name in os.listdir(root):
        fd = posixpath.join(root, name)
        if os.path.isfile(fd) and fd.endswith(suffix):
            names.append(fd)
        if os.path.isdir(fd):
            names.extend(list_files(fd, suffix))
    return names
