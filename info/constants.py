from datetime import timedelta

# 图片验证码Redis有效期， 单位：分钟
IMAGE_CODE_REDIS_EXPIRES = timedelta(minutes=1)

# 短信验证码Redis有效期，单位：分钟
SMS_CODE_REDIS_EXPIRES = timedelta(minutes=1)

# 七牛空间域名 pxu58aa0y.bkt.clouddn.com
QINIU_DOMIN_PREFIX = "http://pxu58aa0y.bkt.clouddn.com/"

# 七牛access_key
access_key = "N6rgp1JyaNmExQFZoBaJ33-cM5wPsPWaxDOgPfW2"

# 七牛secret_key
secret_key = "glfJX27KA6bm70IWSKklpdfKEeH-o4MQ5lrgVfS"

# 七牛存储的名字
bucket_name = "photosxyz"

# 首页展示最多的新闻数量
HOME_PAGE_MAX_NEWS = 10

# 用户的关注每一页最多数量
USER_FOLLOWED_MAX_COUNT = 4

# 用户收藏最多新闻数量
USER_COLLECTION_MAX_NEWS = 10

# 其他用户每一页最多新闻数量
OTHER_NEWS_PAGE_MAX_COUNT = 10

# 点击排行展示的最多新闻数据
CLICK_RANK_MAX_NEWS = 10

# 管理员页面用户每页多最数据条数
ADMIN_USER_PAGE_MAX_COUNT = 10

# 管理员页面新闻每页多最数据条数
ADMIN_NEWS_PAGE_MAX_COUNT = 10
