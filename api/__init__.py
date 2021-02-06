from os import path, environ, pardir
import sys
sys.path.append(pardir)
sys.path.append(path.join(pardir, 'model'))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv
from celery import Celery

from config import Config

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

db = SQLAlchemy()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)


def create_app():
    app = Flask(__name__)
    flask_env = environ.get('FLASK_ENV')
    if flask_env == 'development':
        app.config.from_object('config.DevConfig')
    elif flask_env == 'production':
        app.config.from_object('config.ProdConfig')
    else:
        app.config.from_object('config.ProdConfig')

    db.init_app(app)
    celery.conf.update(app.config)

    from . import api
    app.register_blueprint(api.main)

    with app.app_context():
        from . import api

        db.create_all()
        return app
