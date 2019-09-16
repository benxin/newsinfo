from flask import g, redirect, render_template, request, jsonify, current_app, session

from info import db, constants
from info.models import Category, News
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET
from . import profile_blue


@profile_blue.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    if request.method == 'GET':

        categories = []
        try:

            # 获取所有的分类数据
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
        # 定义列表保存分类数据
        categories_dist = []

        for category in categories:
            # 获取字典
            cate_dict = category.to_dict()
            categories_dist.append(cate_dict)
        # 移除最新分类

        categories_dist.pop(0)
        data = {
            'categories': categories_dist,
        }

        return render_template('news/user_news_release.html', data=data)

    # post提交执行新闻数据发布
    # 获取提交数据字段
    title = request.form.get('title')
    source = '个人发布'
    digest = request.form.get('digest')
    content = request.form.get('content')
    index_image = request.files.get('index_image')
    category_id = request.form.get('category_id')
    # 校验数据是否有值
    if not all([title,source,digest,content,index_image,category_id]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数有误')

    # 尝试读取图片
    try:
        index_image = index_image.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg='参数有误')

    # 将标题图片上传至七牛云
    news = News()
    




@profile_blue.route('/collection')
@user_login_data
def user_collection():
    # 获取页数

    p = request.args.get('p', 1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        p = 1

    user = g.user
    collections = []
    current_page = 1
    total_page = 1
    try:
        # 进行分页数据查询
        paginate = user.collection_news.paginate(p, constants.USER_COLLECTION_MAX_NEWS, False)
        # 获取分页数据
        collections = paginate.items
        # 获取当前分页数据
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    # 收藏列表
    collection_dict_li = []
    for news in collections:
        collection_dict_li.append(news.to_basic_dict())

    data = {
        "total_page": total_page,

        "current_page": current_page,
        "collections": collection_dict_li

    }

    return render_template('news/user_collection.html', data=data)


@profile_blue.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    '''用户密码修改'''
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')

    # 获取请求参数

    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数有误')

    #  获取用户登录信息
    user = g.user
    if not user.check_password(old_password):
        return jsonify(errno=RET.PWDERR, errmsg='原密码不正确')

    # 更新数据
    user.password = new_password

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据提交失败')

    return jsonify(errno=RET.OK, errmsg='数据更新成功')


@profile_blue.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    user = g.user

    data = {

        'user_info': user.to_dict(),
    }
    if request.method == 'GET':
        return render_template('news/user_pic_info.html', data=data)

    # 获取上传文件

    try:
        avatar_file = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='读取文件错误')

    try:
        url = storage(avatar_file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='上传图片失败')

    # 更新图片信息到当前用户
    user.avatar_url = url
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据提交失败')

    return jsonify(errno=RET.OK, data={'avatar_url': constants.QINIU_DOMIN_PREFIX + url})


@profile_blue.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    '''用户个人信息'''
    user = g.user
    if request.method == 'GET':
        data = {

            'user_info': user.to_dict(),
        }

        return render_template('news/user_base_info.html', data=data)

    # 获取参数

    nick_name = request.json.get('nick_name')
    gender = request.json.get('gender')
    signature = request.json.get('signature')

    if not all([nick_name, gender, signature]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    if gender not in (['MAN', 'WOMAN}']):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 更行并储存数据

    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature

    try:
        db.session.commit()
    except BaseException as e:
        current_app.logger.error(e)
        db.session.robllback()
        return jsonify(errno=RET.DBERR, errmsg='数据提交失败')

    # 将session 中的数据实时更新
    session['nick_naem'] = nick_name

    return jsonify(errno=RET.OK, errmsg='更新成功')


@profile_blue.route('/info')
@user_login_data
def get_user_info():
    '''获取用户信息'''

    user = g.user

    if not user:
        return redirect('/')

    data = {

        'user_info': user.to_dict(),
    }
    return render_template('news/user.html', data=data)
