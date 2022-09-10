from os import environ, path
from dotenv import load_dotenv

FLASK_ENV = environ.get('FLASK_ENV', 'development')

basedir = path.abspath(path.dirname(__file__))

if FLASK_ENV == 'development':
    dotenv_file = 'env.dev'
elif FLASK_ENV == 'production':
    dotenv_file = '.env.prod'
elif FLASK_ENV == 'staging':
    dotenv_file = '.env.staging'

load_dotenv(path.join(basedir, dotenv_file))

class Config:
    """Base config."""
    SEND_FILE_MAX_AGE_DEFAULT = 0
    SECRET_KEY = environ.get('SECRET_KEY')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    UPLOAD_EXTENSIONS = ['.csv', '.xls', '.xlsx']
    SQLALCHEMY_TRACK_MODIFICATIONS = environ.get(
        'SQLALCHEMY_TRACK_MODIFICATIONS'
    )
    CELERY_BROKER_URL = environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = environ.get('PROD_DATABASE_URI')

class StagingConfig(Config):
    FLASK_ENV = 'staging'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = environ.get('STAGING_DATABASE_URI')

class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('DEV_DATABASE_URI')
