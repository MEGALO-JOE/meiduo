from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadData

from django.conf import settings
from . import constants


def generate_save_user_openid_token(openid):
    """
    生成保存opened的token,使用itsdangerous
    :param openid:用户扫码后最终获取的openid
    :return:加密完的openid
    """

    # serializer = Serializer(秘钥, 有效期秒)
    serializer = Serializer(settings.SECRET_KEY,constants.ITSDANGEROUS_LIFETIME)

    # serializer.dumps(数据), 返回bytes类型
    data = {"openid":openid}
    access_token_openid = serializer.dumps(data)

    return access_token_openid.decode()

def generate_real_openid(access_token):
    """获取传入的加密的openid并进行解密"""

    serializer = Serializer(settings.SECRET_KEY,constants.ITSDANGEROUS_LIFETIME)

    # 调用loads方法进行解密
    try:
        data = serializer.loads(access_token)
    except BadData:
        return None

    return data.get("openid")