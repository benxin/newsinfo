from datetime import datetime, date, timedelta
import time

from flask import render_template, request, current_app, session, g, redirect, url_for

from info import constants
from info.models import User, News
from . import admin_blue
from info.utils.common import user_login_data


@admin_blue.route('/news_review_detail')
def news_review_detail():
    '''新闻审核'''


@admin_blue.route('/news_review')
def news_review():
    '''待审核新闻列表'''
    page = request.args.get('p', 1)
    keywords = request.values.get('keywords', '')
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list = []
    current_page = 1
    total_page = 1

    try:
        filters = [News.status != 0]
        if keywords:
            filters.append(News.title.contains(keywords))

        # 查询

        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,
                                                                                          constants.ADMIN_NEWS_PAGE_MAX_COUNT,
                                                                                          False)
        news_list = paginate.items
        current_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_review_dict())

    context = {
        'total_page': total_page,
        'current_page': current_page,
        'news_list': news_dict_list
    }
    return render_template('admin/news_review.html', data=context)


@admin_blue.route('/user_list')
def user_list():
    '''获取用户列表'''
    # page = request.values.get('p', 1)
    page = request.args.get('p', 1)

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    users = []
    current_page = 1
    total_page = 1

    # 查询数据
    try:
        paginate = User.query.filter(User.is_admin == False).order_by(User.last_login.desc()).paginate(page,
                                                                                                       constants.ADMIN_USER_PAGE_MAX_COUNT,
                                                                                                       False)
        users = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    # 将模型列表转换成字典列表

    users_list = []

    for user in users:
        users_list.append(user.to_admin_dict())

    data = {
        'total_page': total_page,
        'current_page': current_page,
        'users': users_list
    }

    return render_template('admin/user_list.html', data=data)


@admin_blue.route('/user_count')
def user_count():
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询月新曾数据
    mon_count = 0
    try:
        now = time.localtime()
        mon_begin = '%d-%02d-01' % (now.tm_year, now.tm_mon)
        mon_begin_date = datetime.strptime(mon_begin, '%Y-%m-%d')
        mon_count = User.query.filter(User.is_admin == False, User.create_time >= mon_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询日新增数量

    day_count = 0
    today = date.today()

    try:

        day_begin = today.isoformat()
        day_begin_date = datetime.strptime(day_begin, '%Y-%m-%d')
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询图表信息 获取到当天00:00:00时间

    now_date = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')

    # 定义空列表,保存数据
    active_date = []
    active_count = []

    for i in range(0, 31):
        begin_date = now_date - timedelta(days=i)

        end_day = now_date - timedelta(days=(i - 1))
        active_date.append(begin_date.strftime('%Y-%m-%d'))
        count = 0
        try:
            count = User.query.filter(User.is_admin == False, User.create_time >= begin_date,
                                      User.create_time < end_day).count()

        except Exception as e:
            current_app.logger.error(e)
        active_count.append(count)

    active_date.reverse()
    active_count.reverse()

    data = {
        'total_count': total_count,
        'mon_count': mon_count,
        'day_count': day_count,
        'active_date': active_date,
        'active_count': active_count

    }
    return render_template('admin/user_count.html', data=data)


@admin_blue.route('/index')
@user_login_data
def admin_index():
    '''admin 主页'''

    user = g.user

    if not user:
        return redirect(url_for('admin.admin_login'))

    context = {
        'user': user.to_dict()
    }

    return render_template('admin/index.html', context=context)


@admin_blue.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':

        user_id = session.get('user_id', None)
        is_admin = session.get('is_admin', False)

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
        return render_template('admin/login.html', errmsg='用户名或密码错误')
    if not user.is_admin:
        return render_template('admin/login.html', errmsg='权限不足')

    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile

    if user.is_admin:
        session['is_admin'] = True

    return redirect(url_for('admin.admin_index'))
