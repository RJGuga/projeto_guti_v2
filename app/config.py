import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
    DB_PATH = os.path.join(BASE_DIR, 'guti.db')
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
