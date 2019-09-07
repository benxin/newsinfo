from info.models import User
from . import index_blue
import logging
from flask import render_template, current_app, session


# current_app 是app的代理对象
@index_blue.route('/favicon.ico')
def send_favicon():
    return current_app.send_static_file('news/favicon.ico')


@index_blue.route("/")
def index():
    user_id = session.get("user_id")

    user = None

    if user_id:
        user = User.query.get(user_id)

    data = {
        'user_info': user.to_dict() if user else None,
    }

    return render_template('news/index.html', data=data)
