# -*- coding: utf-8 -*-

import os

from app import create_app
from app.vision.datasets import caltech101
from app.vision.features import bow

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.cli.command()
def extract():
    uris = caltech101.get_caltech101(app.config['DATA_DIR'])
    bow.extract(uris)
