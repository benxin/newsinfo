from flask import render_template, current_app, g, abort, session, request, jsonify
from info.utils.common import user_login_data
from info import constants, db
from info.models import News, User
from info.utils.response_code import RET
from . import news_blue


@news_blue.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    '''新闻收藏'''

    user = g.user
    json_data  = request.json
    news_id = json_data.get('news_id')
    action = json_data.get('action')

    if not user:
        return jsonify(errno=RET.PARAMERR,errmsg='请先登录')
    if not news_id:
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')

    if action not in ("collect","cancel_collect"):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        news = News.query.get(news_id)
    except BaseException  as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg='查询数据失败')

    if not news:
        return jsonify(errno=RET.NODATA,errmsg='新闻数据不存在')

    if action == "collect":
        user.collection_news.append(news)
    else:
        user.collection_news.remove(news)

    try:
        db.session.commit()
    except BaseException as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='数据提交失败')
    return jsonify(errno=RET.OK,errmsg='收藏成功')





@news_blue.route('/<int:news_id>', methods=['GET', 'POST'])
@user_login_data
def news_detail(news_id):
    user = g.user
    # 登录
    # user_id = session.get("user_id")
    # user = None
    #
    # if user_id:
    #     user = User.query.get(user_id)

    # 右侧热门新闻
    news_list = None
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    click_news_list = []
    for news in news_list if news_list else []:
        click_news_list.append(news.to_basic_dict())




    # 新闻详情
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    if not news:
        # 返回数据未找到的页面
        abort(404)

    news.clicks += 1

    # 新闻收藏
    is_collected = False

    if g.user:
        if news in g.user.collection_news:
            is_collected = True





    data = {
        "news": news.to_dict(),
        "is_collected": is_collected,
        "click_news_list": click_news_list,
        "user_info": g.user.to_dict() if g.user else None,
        # 'user_info': user.to_dict() if user else None,
    }
    return render_template('news/detail.html', data=data)
