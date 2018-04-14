# -*- coding: utf-8 -*-

import gzip
import os
import pickle

import numpy

from PIL import Image


# def save_as_image(dict):
#     data = dict['data']
#     data = data.reshape(data.shape[0], 3, 32, 32)
#     filenames = dict['filenames']
#     for index, image in enumerate(data):
#         img0 = Image.fromarray(image[0])
#         img1 = Image.fromarray(image[1])
#         img2 = Image.fromarray(image[2])
#         img = Image.merge("RGB", (img0, img1, img2))
#         img.save("./app/static/uploads/" +
#                  filenames[index].decode('utf8'), "png")


def load_batch(fpath):
    batch = open(fpath, 'rb')
    dict = pickle.load(batch, encoding='bytes')
    # decode utf8
    dict = {k.decode('utf8'): v for k, v in dict.items()}
    save_as_image(dict)
    data = dict['data']
    labels = dict['labels']
    data = data.reshape(data.shape[0], 3, 32, 32)
    return data, labels


def load_cifar():
    path = './app/static/datasets/cifar-10-batches-py'
    num_train_samples = 50000
    x_train = numpy.empty((num_train_samples, 3, 32, 32), dtype='uint8')
    y_train = numpy.empty((num_train_samples,), dtype='uint8')
    print(y_train)
    for i in range(1, 6):
        fpath = os.path.join(path, 'data_batch_' + str(i))
        (x_train[(i - 1) * 10000: i * 10000, :, :, :],
         y_train[(i - 1) * 10000: i * 10000]) = load_batch(fpath)
    return x_train, y_train


if __name__ == "__main__":
    x_train, y_train = load_cifar()
