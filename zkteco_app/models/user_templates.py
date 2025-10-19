# -*- coding: utf-8 -*-
from datetime import datetime

from flask_login import UserMixin
from zkteco_app import db

class UserTemplate(db.Model):
    __tablename__ = "user_templates"

    id = db.Column(db.Integer, primary_key=True)
    #
    device_user_id = db.Column(db.Integer, db.ForeignKey("device_users.uid"), nullable=False)
    device_user = db.relationship("DeviceUser", back_populates="user_template")
    #
    size = db.Column(db.Integer, nullable=False)
    uid = db.Column(db.Integer, nullable=False)
    fid = db.Column(db.Integer, default=0)
    valid = db.Column(db.Integer, default=0)
    template = db.Column(db.LargeBinary, nullable=False)
    write_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
