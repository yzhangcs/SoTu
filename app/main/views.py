# -*- coding: utf-8 -*-

import os
import posixpath

from flask import (current_app, flash, redirect, render_template, request,
                   send_from_directory, url_for)
from werkzeug.utils import secure_filename

from app.utils import download
from app.vision import bof

from . import main
from .forms import ImgForm, URLForm


@main.route('/', methods=['GET', 'POST'])
def index():
    imgform = ImgForm()
    urlform = URLForm()
    cwd = os.getcwd()
    os.chdir(current_app.config['DATA_DIR'])
    upload_dir = 'uploads'

    if imgform.validate_on_submit():
        file = imgform.fileimg.data
        filename = secure_filename(file.filename)
        uri = posixpath.join(upload_dir, filename)
        if not os.path.exists(uri):
            file.save(uri)
        return redirect(url_for('.result', uri=uri))
    elif urlform.validate_on_submit():
        url = urlform.txturl.data
        filename = secure_filename(url.split('/')[-1])
        uri = posixpath.join(upload_dir, filename)
        download(url, upload_dir, filename)
        if not os.path.exists(uri):
            flash('无法取回指定URL的图片')
            return redirect(url_for('.index'))
        else:
            return redirect(url_for('.result', uri=uri))
    os.chdir(cwd)
    return render_template('index.html')


@main.route('/result', methods=['GET'])
def result():
    uri = request.args.get('uri')
    images = bof.match(uri, top_k=30)
    return render_template('result.html', uri=uri, images=images)


@main.route('/images/<path:uri>')
def download_file(uri):
    return send_from_directory(current_app.config['DATA_DIR'],
                               uri, as_attachment=True)
