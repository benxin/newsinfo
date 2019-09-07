from logging.handlers import RotatingFileHandler
import logging
from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from redis import Redis

from config import config, Config
from flask_wtf.csrf import generate_csrf

def setup_log(config_name):

    # 设置日志记录等级
    logging.basicConfig(level=Config.LOG_LEVEL)
    # 日志存放路径,每个日志的文件大小上限,保存日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10,encoding='utf-8')
    # file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100,backupCount=10)
    # 日志的格式
    logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    # 为创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(logging_format)
    # 设置全局日志工具对象



    logging.getLogger().addHandler(file_log_handler)
    # 创建数据库对象


db = SQLAlchemy()


def create_app(config_name):
    setup_log(config_name)
    app = Flask(__name__)
    app.config.from_object(config[config_name])


    # db = SQLAlchemy(app)
    db.init_app(app)

    manager = Manager(app)
    Migrate(app, db)
    manager.add_command('db', MigrateCommand)


    # 开启CSRF保护
    CSRFProtect(app)
    Session(app)

    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie('csrf_token',csrf_token)
        return response


    # 注册index蓝本
    from info.index import index_blue
    app.register_blueprint(index_blue)

    # 注册登录蓝本
    from info.passport import passport_blue
    app.register_blueprint(passport_blue)
    return app
