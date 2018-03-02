# -*- coding: utf-8 -*-

import os
import urllib.request

from flask import current_app, flash, redirect, render_template, url_for
from werkzeug.utils import secure_filename

from . import main
from .forms import ImgForm, URLForm


@main.route('/', methods=['GET', 'POST'])
def index():
    imgform = ImgForm()
    urlform = URLForm()
    if imgform.validate_on_submit():
        file = imgform.fileimg.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_DIR'], filename)
        if not os.path.exists(filepath):
            file.save(filepath)
        return redirect(url_for('.result'))
    elif urlform.validate_on_submit():
        url = urlform.txturl.data
        filename = url.split('/')[-1]
        filepath = os.path.join(current_app.config['UPLOAD_DIR'], filename)
        try:
            urllib.request.urlretrieve(url, filepath)
        except Exception as e:
            flash('无法取回指定URL的图片')
            return redirect(url_for('.index'))
        return redirect(url_for('.result'))
    return render_template('index.html')


@main.route('/result', methods=['GET', 'POST'])
def result():
    images = []
    for img in os.listdir(current_app.config['UPLOAD_DIR'])[:20]:
        images.append(img)
    return render_template('result.html', images=images)
