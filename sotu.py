# -*- coding: utf-8 -*-

import os

from flask_migrate import Migrate

from sotu import create_app, db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
