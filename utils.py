# -*- coding: utf-8 -*-

import os
import posixpath
import zipfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlretrieve


def download(root, filename, url):
    fpath = os.path.join(root, filename)
    if not os.path.exists(root):
        os.mkdir(root)
    if os.path.exists(fpath):
        print("Data already downloaded")
    else:
        print("Downloading %s to %s" % (url, fpath))
        err_msg = "URL fetch failure on {}: {} -- {}"
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


def unzip(root, filename, path):
    fpath = os.path.join(root, filename)
    with zipfile.ZipFile(fpath, 'r') as zf:
        zf.extractall(path=os.path.join(root, path))


def list_files(root, suffix):
    names = []
    for name in os.listdir(root):
        fd = posixpath.join(root, name)
        if os.path.isfile(fd) and fd.endswith(suffix):
            names.append(fd)
        if os.path.isdir(fd):
            names.extend(list_files(fd, suffix))
    return names
