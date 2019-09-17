from flask import render_template, current_app, session, request, jsonify, g

from info import constants
from info.models import User, News, Category
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import index_blue


@index_blue.route('/news_list')
def news_list():
    # 新闻列表
    cid = request.args.get('cid', "1")
    page = request.args.get('page', "1")
    per_page = request.args.get('per_page', constants.HOME_PAGE_MAX_NEWS)

    try:
        page = int(page)
        cid = int(cid)
        per_page = int(per_page)
    except Exception as e:
        cid = 1
        page = 1
        per_page = 10

    filter = []

    if cid != 1:
        filter.append(News.category_id == cid)

    paginate = News.query.filter(*filter).order_by(News.create_time.desc()).paginate(page, per_page, False)

    items = paginate.items
    # 总页数
    current_page = paginate.page
    # 表示总页数
    total_page = paginate.pages

    news_list = []
    for item in items:
        news_list.append(item.to_basic_dict())

    # 查询数据并分页
    filters = [News.status == 0]
    # 如何分页不为0,那么就添加分类id 的过滤
    if cid != '0':
        filters.append(News.category_id == cid)

    data = {
        'current_page': current_page,
        'total_page': total_page,
        'news_dict_li': news_list

    }
    return jsonify(errno=RET.OK, errmsg='ok', data=data)


@index_blue.route("/")
@user_login_data
def index():
    user = g.user


    # 热门新闻

    news = News.query.order_by(News.clicks.desc()).limit(10)
    news_list = []

    for new_model in news:
        news_list.append(new_model.to_dict())

    # 新闻分类标题

    categorys = Category.query.all()
    category_list = []
    for category in categorys:
        category_list.append(category.to_dict())

    data = {
        'user_info': user.to_dict() if user else None,
        "click_news_list": news_list,
        "categories": category_list

    }

    return render_template('news/index.html', data=data)


# current_app 是app的代理对象
@index_blue.route('/favicon.ico')
def send_favicon():
    return current_app.send_static_file('news/favicon.ico')
