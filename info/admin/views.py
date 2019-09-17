from flask import render_template, request, current_app, session, g, redirect, url_for

from info.models import User
from . import admin_blue
from info.utils.common import user_login_data


@admin_blue.route('/index')
@user_login_data
def admin_index():
    '''管理员主页'''

    user = g.user

    if not user:
        return redirect(url_for('admin.admin_login'))

    context = {
        'user': user.to_dict()
    }

    return render_template('admin/index.html', context=context)


@admin_blue.route('/login', methods=['GET', 'POST'])
def admin_login():
    user = g.user
    if request.method == 'GET':

        user_id = session.get('user_id',None)
        is_admin = session.get('is_admin',False)

        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))
        return render_template('admin/login.html')


    # 获取登录参数
    username = request.form.get('username')
    password = request.form.get('password')

    if not all([username, password]):
        return render_template('admin/login.html', errmsg='参数不足')

    try:
        user = User.query.filter(User.mobile == username).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg='数据查询失败')

    if not user:
        return render_template('admin/login.html', errmsg="用户不存在")

    if not user.check_password(password):
        return render_template('admin/login.html', errmsg='密码错误')
    if not user.is_admin:
        return render_template('admin/login.html', errmsg='权限不足')

    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile

    if user.is_admin:
        session['is_admin'] = True

    return redirect(url_for('admin.admin_index'))
