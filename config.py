import os
from datetime import timedelta
import logging

from redis import Redis

DB_NAME = os.getenv('dbname')


class Config(object):
    DEBUG = True
    # ssl_context = ('localhost.pem', 'localhost-key.pem')
    DB_NAME = os.getenv('dbname')

    DB_PWD = os.getenv('dbpwd')

    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@localhost/information'.format(DB_NAME, DB_PWD)

    LOG_LEVEL = logging.DEBUG
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis 配置
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0

    SECRET_KEY = '4098a3d1aaf047fbb2f6267888fd1bc8'

    # flask_session 配置
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = Redis(host=REDIS_HOST, port=REDIS_PORT)

    PERMANENT_SESSION_LIFETIME = timedelta(days=2)

    redis_db = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, charset="utf-8", decode_responses=True)

    @staticmethod
    def init_app():
        pass


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.ERROR


class DevelopmentConfig(Config):
    DEBUG = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
