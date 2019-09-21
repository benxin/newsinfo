import functools

from flask import session, g

from info.models import User


def do_class_index(index):
    if index == 0:
        return "first"
    elif index == 1:
        return "second"
    elif index == 2:
        return "third"
    else:
        return ""


def user_login_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        user = None
        if user_id:
            user = User.query.get(user_id)
        g.user = user
        return func(*args,**kwargs)

    return wrapper
