from flask import render_template, current_app, g, abort, request, jsonify

from info import constants, db
from info.models import News, Comment, CommentLike, User
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import news_blue


@news_blue.route('/followed_user', methods=['GET', 'POST'])
@user_login_data
def followed_user():
    user = g.user
    user_id = request.json.get('user_id')
    action = request.json.get('action')
    news_user = User.query.get(user_id)
    if action == 'follow':
        if news_user not in user.followed:
            user.followed.append(news_user)
        else:
            return jsonify(errno=RET.PARAMERR, errmsg='已经关注,请勿重复操作')
    else:
        if news_user in user.followed:
            user.followed.remove(news_user)
        else:
            return jsonify(errno=RET.PARAMERR, errmsg='为关注的用户无法执行取消关注')
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg='ok')


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

    # 查询首页右边的热门排行新闻数据
    news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)

    news_list = []

    for new_model in news:
        news_list.append(new_model.to_dict())

    # 根据新闻id获取到详情页面的数据
    news_content = News.query.get(news_id)

    # 当前新闻是否被收藏,一般默认情况下,第一次进来默认值肯定是false
    is_collection = False
    # 如果user有值,说明用户已经登陆
    if user:
        # 判断当前新闻,是否在当前用户的新闻收藏列表里面
        if news_content in user.collection_news:
            is_collection = True

    # 获取到新闻的评论列表
    comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    # 所有的点赞数据
    comment_likes = []
    # 所有的点赞id
    comment_likes_ids = []
    if user:
        comment_likes = CommentLike.query.filter(CommentLike.user_id == user.id).all()
        comment_likes_ids = [comment_like.comment_id for comment_like in comment_likes]

    comments_list = []

    for comment in comments:
        comment_dict = comment.to_dict()
        if comment.id in comment_likes_ids:
            comment_dict['is_like'] = True
        comments_list.append(comment_dict)

    # 判断用户是否关注
    is_followed = False

    # 当前新闻必须有作者,才能关注, 用户必须登陆,才能关注作者

    if user:
        # 判断当前新闻的作者是否在我关注的人的列表里面(张三,李四)
        if news_content.user in user.followed:
            is_followed = True

    data = {
        "user_info": user.to_dict() if user else None,
        "click_news_list": news_list,
        "news": news_content.to_dict(),
        "is_collected": is_collection,
        "comments": comments_list,
        "is_followed": is_followed
    }
    return render_template('news/detail.html', data=data)
