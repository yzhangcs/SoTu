# -*- coding: utf-8 -*-

from . import db


class Image(db.Model):
    __tablename__ = 'images'
    uri = db.Column(db.Text, primary_key=True)
    filename = db.Column(db.String)
    # HSV = db.Column(db.Text)
    # SIFT = db.Column(db.Text)

    def __repr__(self):
        return '<Image %r>' % self.filename
