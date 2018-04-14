# -*- coding: utf-8 -*-

import os
import pickle
import tarfile
import urllib.request

import numpy
from flask import current_app

import downloader


def unpickle(filename):
    file = open(filename, 'rb')
    dict = pickle.load(file, encoding='bytes')
    file.close()
    return dict


def download_cifar10():
    url = 'http://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz'
    local = os.path.join(
        current_app.config['CIFAR10_DIR'], 'cifar-10-python.tar.gz')
    downloader.download(url, local)
    if os.path.exists(local):
        downloader.untar(local, current_app.config['CIFAR10_DIR'], remove=True)


def load_cifar():
    if not os.path.exists(current_app.config['CIFAR10_DIR']):
        download_cifar10()
    for batch_idx in numpy.arange(5):
        data_path = '../data/cifar/cifar-10-batches-py/data_batch_%d' % (
            batch_idx + 1)
        data_batch = unpickle(data_path)
        sub_data = data_batch['data']
        sub_labels = numpy.array(data_batch['labels'])
        if batch_idx == 0:
            data = sub_data
            labels = sub_labels
        else:
            data = numpy.vstack((data, sub_data))
            labels = numpy.hstack((labels, sub_labels))
    labels = labels.reshape((-1, 1))
    return data, labels

    num_train_samples = 50000
    x_train = numpy.empty((num_train_samples, 3, 32, 32), dtype='uint8')
    y_train = numpy.empty((num_train_samples,), dtype='uint8')
    print(y_train)
    for i in range(1, 6):
        fpath = os.path.join(path, 'data_batch_' + str(i))
        (x_train[(i - 1) * 10000: i * 10000, :, :, :],
         y_train[(i - 1) * 10000: i * 10000]) = load_batch(fpath)
    return x_train, y_train


def load_cifar():
    data = './app/static/datasets/cifar-10-batches-py'
    num_train_samples = 50000
    x_train = numpy.empty((num_train_samples, 3, 32, 32), dtype='uint8')
    y_train = numpy.empty((num_train_samples,), dtype='uint8')
    print(y_train)
    for i in range(1, 6):
        fpath = os.path.join(path, 'data_batch_' + str(i))
        (x_train[(i - 1) * 10000: i * 10000, :, :, :],
         y_train[(i - 1) * 10000: i * 10000]) = load_batch(fpath)
    return x_train, y_train
