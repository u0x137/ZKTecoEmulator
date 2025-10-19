# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'zkteco_app'
    app.config['UPLOAD_FOLDER'] = './zkteco_app/uploads'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zkteco.db'
    db.init_app(app)
    
    from . import models
    from .controllers import routes as routes_blueprint
    app.register_blueprint(routes_blueprint)
    return app

app = create_app()

with app.app_context():
    db.create_all()
