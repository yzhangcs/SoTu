# -*- coding: utf-8 -*-

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from config import config
from vision import BoF

bof = BoF()
csrf = CSRFProtect()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bof.init_app(app)
    csrf.init_app(app)
    # 注册蓝本
    from .main import main
    app.register_blueprint(main)
    return app
