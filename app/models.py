# -*- coding: utf-8 -*-

from flask import current_app

from app import db
from app.vision.datasets import get_caltech101


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.Text, unique=True)

    def __init__(self, **kwargs):
        super(Image, self).__init__(**kwargs)

    @staticmethod
    def insert_caltech101():
        images = get_caltech101(current_app.config['DATA_DIR'])
        for uri in images:
            img = Image.query.filter_by(uri=uri).first()
            if img is None:
                db.session.add(Image(uri=uri))
        db.session.commit()

    def __repr__(self):
        return '<Image %r>' % self.uri
