# -*- coding: utf-8 -*-

from flask import current_app

from . import db
from .utils import data_loader


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.Text, unique=True)
    filename = db.Column(db.String, nullable=True)

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)

    @staticmethod
    def insert_cifar10():
        images = data_loader.load_cifar10()
        for uri, filename in images:
            img = Image.query.filter_by(uri=uri).first()
            if img is None:
                img = Image(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Image %r>' % self.filename
