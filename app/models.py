# -*- coding: utf-8 -*-

from flask import current_app

from . import db
from .utils import cifar10


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.Text, unique=True)

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)

    @staticmethod
    def insert_cifar10():
        images = cifar10.get_training_images()
        for uri in images:
            img = Image.query.filter_by(uri=uri).first()
            if img is None:
                db.session.add(Image(uri=uri))
        db.session.commit()

    def __repr__(self):
        return '<Image %r>' % self.filename
