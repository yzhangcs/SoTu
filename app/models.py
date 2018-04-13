# -*- coding: utf-8 -*-

from . import db


class Image(db.Model):
    uri = db.Column(db.Text, primary_key=True)
    filename = db.Column(db.String, nullable=True)
    # HSV = db.Column(db.Text)
    # SIFT = db.Column(db.Text)

    def __repr__(self):
        return '<Image %r>' % self.filename
