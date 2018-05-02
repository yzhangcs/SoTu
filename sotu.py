# -*- coding: utf-8 -*-

import os

from app import bof, create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.cli.command()
def extract():
    bof.extract()
