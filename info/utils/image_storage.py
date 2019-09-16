import logging

from qiniu import Auth,put_data

# access key and Secret key

access_key = 'N6rgp1JyaNmExQFZoBaJ33-cM5wPsPWaxDOgPfW2'

secret_key =  'EglfJX27KA6bm70IWSKklpdfKEeH-o4MQ5lrgVfS'


bucket_name = 'photosxyz'
# pxu58aa0y.bkt.clouddn.com


def storage(data):
    if not data:
        return None

    try:
        # 创建授权对象

        q = Auth(access_key,secret_key)

        # 生成token
        token = q.upload_token(bucket_name)
        ret,info = put_data(token,None,data)

    except Exception as e:
        logging.error(e)
        raise e


    if info  and info.status_code != 200:
        raise Exception('上传失败')
    # 返回七牛云保存的图片名,图片也是路径访问七牛云图片的路径
    return ret['key']

if __name__ == '__main__':
    file_name = input('请输入上传的文件')
    with open(file_name,'rb') as f:
        storage(f.read())




