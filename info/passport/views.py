from datetime import datetime
import re
from random import randint
from flask import request, make_response, jsonify, current_app, session

from info.models import User
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import passport_blue
from config import Config
from info import constants
from info import db


# 登出
@passport_blue.route('/logout', methods=['GET', 'POST'])
def logout():
    # 删除session数据
    session.pop('user_id',None)
    session.pop('nick_name',None)
    session.pop('mobile',None)
    return jsonify(errno = RET.OK,errmsg = '退出成功')






# 登录

@passport_blue.route('/login', methods=['GET', 'POST'])
def login():
    mobile = request.json.get("mobile")
    password = request.json.get('password')

    # # 通过手机号查询用户
    # if not all([mobile, password]):
    #     return jsonify(errno=RET.PARAMERR, errmsg='请输入用户名或密码')

    try:

        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询出错')

    if not user:

        return jsonify(errno = RET.USERERR, errmsg='用户不存在')

    if not user.check_password(password):
        return jsonify(errno=RET.PWDERR, errmsg='密码错误')

    # 更新登录时间
    user.last_login = datetime.now()
    # 提交数据到数据库
    db.session.commit()


    # 用户状态保持

    session["mobile"] = user.mobile
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name

    return jsonify(errno= RET.OK, errmsg='登录成功')






# 注册

@passport_blue.route('/register', methods=['GET', 'POST'])
def register():
    mobile = request.json.get('mobile')
    smscode = request.json.get("smscode")
    password = request.json.get("password")

    if not all([mobile,smscode,password]):
        return jsonify(errno = RET.PARAMERR,errmsg = '参数错误')

    real_sms_code = Config.redis_db.get("sms_code_" + mobile)

    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码已过期')
    if smscode != real_sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg="短信验证码错误")

    # 创建用户对象

    user = User()
    user.mobile = mobile
    user.password = password
    user.nick_name = mobile

    # 获取当前时间，用来注册
    user.last_login = datetime.now()

    # 将用户数据写入数据库
    db.session.add(user)
    db.session.commit()
    return jsonify(errno=RET.OK, errmsg='注册成功')



 # 发送短信验证码
@passport_blue.route("/sms_code", methods=["GET", "POST"])
def sms_code():
    # 获取前端传递的mobile ,imaget_code,imaget_code_id参数

    mobile = request.json.get('mobile')
    image_code = request.json.get('image_code')
    image_code_id = request.json.get('image_code_id')

    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="请输入参数")

    if not re.match('1[3456789]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号码无效")

    real_image_code = Config.redis_db.get("image_code_" + image_code_id)

    # 校验验证码是否过期
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已过期")

    # 校验验证码是否正确
    if image_code.lower() != real_image_code.lower():
        return jsonify(errno=RET.PARAMERR, errmsg="验证码错误")

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询错误')

    # 校验手机好是否注册
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg='手机号已被注册')

    # 生成验证码
    random_sms_code = "{:0<6d}".format(randint(0, 999999))
    print(random_sms_code)

    # mobile 参数表示key
    # random_sms_code 参数表示随机数
    # constants.SMS_CODE_REDIS_EXPIRES 参数表示过期时间

    Config.redis_db.set("sms_code_" + mobile, random_sms_code, constants.SMS_CODE_REDIS_EXPIRES)


    return jsonify(errno=RET.OK, errmsg='短信验证码发送成功')




@passport_blue.route("/image_code")
def image_code():
    code_id = request.args.get('code_id')
    # name 图片验证码的名字
    # text 图片验证码的内容
    # image 图片
    # 生成图片验证码
    name, text, image = captcha.generate_captcha()


    print("验证码：" + text)

    # code_id 表示key
    # text 表示图片验证码
    # image表示图片

    Config.redis_db.set("image_code_" + code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)

    # make_repsonse: 表示响应体，这个对象的参数表示图片验证码
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response
