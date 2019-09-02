import os
from datetime import timedelta
import logging

from redis import Redis


class Config(object):
    DEBUG = True
    DB_NAME = os.getenv('dbname')
    DB_PWD = os.getenv('dbpwd')
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:benxin@localhost/information'
    SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@localhost/information'.format(DB_NAME,DB_PWD)
    LOG_LEVEL = logging.DEBUG
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    SECRET_KEY = 'eac33e0f-ca5f-498e-b64d-9f45ea53aaea'

    # flask_session 配置
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = Redis(host=REDIS_HOST, port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)

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
