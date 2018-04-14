# -*- coding: utf-8 -*-

import logging
import os
import tarfile
from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve


def untar(tarname, path, remove=False):
    with tarfile.open(tarname) as tar:
        tar.extractall(path=path)
    if remove:
        os.remove(tarname)


def download(url, path, untar=False):
    print('Downloading data from ', url)
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
