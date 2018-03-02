# -*- coding: utf-8 -*-

import os


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'it is a secret'
    UPLOAD_DIR = os.path.join(BASE_DIR, 'app/static/uploads')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'default': Config
}
