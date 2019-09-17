from flask import render_template, current_app, g, abort, request, jsonify

from info import constants, db
from info.models import News, Comment, CommentLike, User
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import news_blue


@news_blue.route('/comment_like', methods=['POST'])
@user_login_data
def set_comment_like():
    '''评论点赞'''

    if not g.user:
        return jsonify(errno=RET.SESSIONERR, errmsg='请登录')

    # 获取参数

    comment_id = request.json.get('comment_id')
    action = request.json.get('action')
    news_id = request.json.get('news_id')

    # 判断参数

    if not all([comment_id, news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if action not in ('add', 'remove'):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 查询评论

    try:
        comment = Comment.query.get(comment_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询失败')

    if not comment:
        return jsonify(errno=RET.NODATA, errmsg='评论数据不存在')

    if action == 'add':
        comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=g.user.id).first()
        if not comment_like:
            comment_like = CommentLike()
            comment_like.comment_id = comment_id
            comment_like.user_id = g.user.id
            db.session.add(comment_like)
            # 增加点赞条数
            comment.like_count += 1
    else:
        comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=g.user.id).first()
        if comment_like:
            db.session.delete(comment_like)
            # 减少点赞条数
            comment.like_count -= 1

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='操作失败')

    return jsonify(errno=RET.OK, errmsg='操作成功')


@news_blue.route('/news_comment', methods=['POST'])
@user_login_data
def add_news_comment():
    # 评论

    user = g.user
    if not user:
        return jsonify(errno=RET.SERVERERR, errmsg='未登录')

    # 获取参数
    data_dict = request.json
    news_id = data_dict.get('news_id')
    comment_str = data_dict.get("comment")
    parent_id = data_dict.get("parent_id")

    if not all([news_id, comment_str]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不足')

    try:
        news = News.query.get(news_id)
    except BaseException as e:
        return jsonify(errno=RET.DBERR, errmsg='数据查询失败')

    if not news:
        return jsonify(errno=RET.NODATA, errmsg='新闻不存在')

    # 保存数据
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news.id
    comment.content = comment_str

    if parent_id:
        comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存评论数据失败')

    return jsonify(errno=RET.OK, errmsg='评论成功', data=comment.to_dict())


@news_blue.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    '''新闻收藏'''

    user = g.user

    news_id = request.json.get('news_id')
    action = request.json.get('action')

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg='请先登录')
    if not news_id:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    if action not in ("collect", "cancel_collect"):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        news = News.query.get(news_id)
    except BaseException  as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')

    if not news:
        return jsonify(errno=RET.NODATA, errmsg='新闻数据不存在')

    if action == "collect":
        user.collection_news.append(news)
    else:
        user.collection_news.remove(news)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据提交失败')
    return jsonify(errno=RET.OK, errmsg='收藏成功')


@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    user = g.user

    # 右侧热门新闻
    news_list = None
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    click_news_list = []

    for news in news_list if news_list else []:
        click_news_list.append(news.to_dict())

    # 新闻详情
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    # 新闻收藏
    # 判断用户是否收藏过新闻
    is_collected = False

    if user:
        if news in user.collection_news:
            is_collected = True

    if not news:
        # 返回数据未找到的页面
        abort(404)

    news.clicks += 1

    # 新闻评论列表
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.lgger.error(e)

    comment_like_ids = []

    if user:
        try:
            comment_ids = [comment.id for comment in comments]
            if len(comment_ids) > 0:
                # 获取当前新闻的所有评论点赞记录
                comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),
                                                         CommentLike.user_id == g.user.id).all()

                comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            current_app.logger.error(e)

    comment_list = []

    for item in comments if comments else []:
        comment_dict = item.to_dict()
        comment_dict['is_like'] = False

        if g.user and item.id in comment_like_ids:
            comment_dict['is_like'] = True
        comment_list.append(comment_dict)



    # 当前用户是否关注当前新闻作者

    is_followed = False



    #     if news.user.followers.filter(User.id == g.user.id).count() > 0:
    #         is_followed = True

    data = {

        "user_info": user.to_dict() if user else None,
        "click_news_list": click_news_list,
        "news": news,
        "is_collected": is_collected,
        'comments': comment_list,
        # 'is_followed': is_followed,
    }

    return render_template('news/detail.html', data=data)
