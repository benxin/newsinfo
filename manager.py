import os

from flask import current_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Server
from info import create_app, db
from info import models
from info.models import User

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))

app = create_app("development")
manager = Manager(app)
Migrate(app, db)
server = Server(host="0.0.0.0", port=4000, ssl_crt='cert.pem', ssl_key='key.pem')

# server =Server(host='127.0.0.1', port=5000,  ssl_crt='cert.pem', ssl_key='key.pem' )
manager.add_command("runserver", server)
manager.add_command('db', MigrateCommand)


@manager.option('-n', '-name', dest='name')
@manager.option('-p', '-password', dest='password')
def createsuperuser(name, password):
    if not all([name, password]):
        return

    user = User()
    user.mobile = name
    user.nick_name = name
    user.password = password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        print(e)
        db.session.rollback()


if __name__ == '__main__':
    manager.run()
