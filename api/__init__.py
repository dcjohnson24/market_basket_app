from os import path, environ, pardir
import sys
sys.path.append(pardir)
sys.path.append(path.join(pardir, 'model'))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


sentry_sdk.init(
    dsn="https://435a5d9c92bc4b64ae9c8541c3949fe9@o502892.ingest.sentry.io/5586353",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

db = SQLAlchemy()


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

    from . import api
    app.register_blueprint(api.main)

    with app.app_context():
        from . import api

        db.create_all()
        return app
