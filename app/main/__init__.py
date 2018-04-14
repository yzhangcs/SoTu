# -*- coding: utf-8 -*-

from flask import Blueprint

main = Blueprint('main', __name__)
# 避免循环导入依赖
from . import views, errors
