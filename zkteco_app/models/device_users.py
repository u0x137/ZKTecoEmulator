# -*- coding: utf-8 -*-
from datetime import datetime

from flask_login import UserMixin
from zkteco_app import db

class DeviceUser(UserMixin, db.Model):
    __tablename__ = "device_users"

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, unique=True, nullable=False)
    privilege = db.Column(db.Integer, default=0)
    password = db.Column(db.String(100), default="")
    name = db.Column(db.String(100), nullable=False)
    card = db.Column(db.Integer, default=0)
    group_id = db.Column(db.Integer)                          ###To str
    timezone = db.Column(db.String(50), default="")
    user_id = db.Column(db.Integer, unique=True)              ###To str
    user_template = db.relationship("UserTemplate", back_populates="device_user") 
    user_attendance = db.relationship("UserAttendance", back_populates="device_user") 
    write_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
