# -*- coding: utf-8 -*-

import os


class Config:
    DEBUG = False
    # 路径配置
    BASE_DIR = os.path.dirname(__file__)
    UPLOAD_DIR = os.path.join(BASE_DIR, 'app/static/uploads')
    # 秘钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'it is a secret'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
