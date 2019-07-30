import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'
    SECRET_KEY = os.getenv('SECRET_KEY')
    POST_PER_PAGE = 10

class DevConfig(Config):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

class ProdConfig(Config):
    pass

config = {
    'development'   : DevConfig,
    'production'    : ProdConfig,

    'default'       : DevConfig
}