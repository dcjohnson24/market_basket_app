from os import path, environ, pardir
import sys
sys.path.append(pardir)
sys.path.append(path.join(pardir, 'model'))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv
from celery import Celery

from config import Config

FLASK_ENV = environ.get('FLASK_ENV', 'development')

basedir = path.abspath(path.dirname(__file__))
if FLASK_ENV == 'development':
    load_dotenv(path.join(basedir, '.env.dev'))
elif FLASK_ENV == 'production':
    load_dotenv(path.join(basedir, '.env.prod'))


if FLASK_ENV == 'production':
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn="https://435a5d9c92bc4b64ae9c8541c3949fe9@o502892.ingest.sentry.io/5586353",
        integrations=[FlaskIntegration(), RedisIntegration()],
        traces_sample_rate=1.0
    )


db = SQLAlchemy()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)


def create_app():
    app = Flask(__name__)
    if FLASK_ENV == 'development':
        app.config.from_object('config.DevConfig')
    elif FLASK_ENV == 'production':
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
