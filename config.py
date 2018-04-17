# -*- coding: utf-8 -*-

import os


class Config:
    # 路径配置
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    IMAGE_DIR = os.path.join(BASE_DIR, 'images')
    UPLOAD_DIR = os.path.join(IMAGE_DIR, 'uploads')
    # 秘钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'it is a secret'
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'sotu.db')

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
