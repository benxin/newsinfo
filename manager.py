import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Server

from info import create_app, db
from info import models
app = create_app("development")



ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))

manager = Manager(app)
Migrate(app, db)
server = Server(host="0.0.0.0", port=4000, ssl_crt='cert.pem',ssl_key='key.pem')

# server =Server(host='127.0.0.1', port=5000,  ssl_crt='cert.pem', ssl_key='key.pem' )
manager.add_command("runserver", server)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()




