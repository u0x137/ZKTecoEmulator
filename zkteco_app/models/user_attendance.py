# -*- coding: utf-8 -*-
from datetime import datetime, timezone

from flask_login import UserMixin
from zkteco_app import db



class UserAttendance(db.Model):
    __tablename__ = "user_attendance"

    id = db.Column(db.Integer, primary_key=True)
    device_user_id = db.Column(db.Integer, db.ForeignKey("device_users.id"), nullable=False)
    device_user = db.relationship("DeviceUser", back_populates="user_attendance")
    uid = db.Column(db.Integer, nullable=False)    # User ID
    status = db.Column(db.Integer, default=1)                   # Status (check-in/out)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) # TODO: TimeZone Naive
    punch = db.Column(db.Integer, default=0)                    # Punch type
    user_id = db.Column(db.String(50), nullable=False)          # External user ID
    reserved = db.Column(db.String(50), default="")             # Reserved field
    workcode = db.Column(db.String(50), default="")             # Work code
    space = db.Column(db.String(50), default="")
    write_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
