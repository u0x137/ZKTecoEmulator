# -*- coding: utf-8 -*-
from datetime import datetime

from flask_login import UserMixin
from zkteco_app import db

class DeviceSettings(UserMixin, db.Model):
    __tablename__ = "device_settings"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    timezone = db.Column(db.String(50), default="")
    host = db.Column(db.String(100), default="0.0.0.0")
    port = db.Column(db.Integer, default=4370)
    timeout = db.Column(db.Integer, default=3)
    protocol = db.Column(db.String(100), default="TCP")
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    is_punch_enabled = db.Column(db.Boolean, default=True, nullable=False)
    write_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
