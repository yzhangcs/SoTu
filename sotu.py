# -*- coding: utf-8 -*-

import os

from app import create_app
from app.vision.datasets import holidays
from app.vision import bof

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.cli.command()
def extract():
    uris = holidays.get_holidays(app.config['DATA_DIR'])
    bof.extract(uris)
