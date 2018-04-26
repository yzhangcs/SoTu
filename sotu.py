# -*- coding: utf-8 -*-

import os

from app import create_app
from app.vision.datasets import corel1k
from app.vision import bof

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.cli.command()
def extract():
    uris = corel1k.get_corel1k(app.config['DATA_DIR'])
    bof.extract(uris)
