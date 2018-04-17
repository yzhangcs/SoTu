# -*- coding: utf-8 -*-

import os

from flask import (current_app, flash, redirect, render_template,
                   send_from_directory, url_for)
from werkzeug.utils import secure_filename

from app import db
from app.models import Image
from app.utils import download

from . import main
from .forms import ImgForm, URLForm


@main.route('/', methods=['GET', 'POST'])
def index():
    imgform = ImgForm()
    urlform = URLForm()
    upload_dir = 'uploads'
    if imgform.validate_on_submit():
        file = imgform.fileimg.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(
            current_app.config['IMAGE_DIR'], upload_dir, filename)
        if not os.path.exists(filepath):
            file.save(filepath)
        insert_to_db(os.path.join(upload_dir, filename))
        return redirect(url_for('.result'))
    elif urlform.validate_on_submit():
        url = urlform.txturl.data
        filename = secure_filename(url.split('/')[-1])
        filepath = os.path.join(
            current_app.config['IMAGE_DIR'], upload_dir, filename)
        download(url,
                 os.path.join(current_app.config['IMAGE_DIR'], upload_dir),
                 filename)
        if not os.path.exists(filepath):
            flash('无法取回指定URL的图片')
            return redirect(url_for('.index'))
        else:
            insert_to_db(os.path.join(upload_dir, filename))
            return redirect(url_for('.result'))
    return render_template('index.html')


@main.route('/result', methods=['GET', 'POST'])
def result():
    images = [img.uri for img in Image.query.limit(30)]
    return render_template('result.html', images=images)


@main.route('/images/<path:filename>')
def download_file(filename):
    return send_from_directory(current_app.config['IMAGE_DIR'],
                               filename, as_attachment=True)


def insert_to_db(uri):
    if not os.path.exists(uri):
        return
    db.session.add(Image(uri=uri))
    db.session.commit()
