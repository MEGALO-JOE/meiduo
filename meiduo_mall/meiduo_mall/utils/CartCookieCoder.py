import base64
import pickle


def set_cart_cookie_str(carts_dict):
    """设置cart的cookie"""

    # # 先将字典转换成bytes类型
    # cart_bytes = pickle.dumps(carts_dict)
    # # 再将bytes类型转换成bytes类型的字符串
    # cart_str_bytes = base64.b64encode(cart_bytes)
    # # 把bytes类型的字符串转换成字符串
    # cookie_carts_str = cart_str_bytes.decode()

    # cookie_carts_str = base64.b64encode(pickle.dumps(carts_dict)).decode()

    # 先将字典转换成bytes类型
    cart_bytes = pickle.dumps(carts_dict)
    # 再将bytes类型转换成bytes类型的字符串
    cart_str_bytes = base64.b64encode(cart_bytes)
    # 把bytes类型的字符串转换成字符串
    cookie_carts_str = cart_str_bytes.decode()


    return cookie_carts_str

def get_cart_cookie_dict(carts_str):
    """根据cookie中的cart获取carts_dict"""
    # # 把字条串转换成bytes类型的字符串
    cart_str_bytes = carts_str.encode()
    # 把bytes类型的字符串转换成bytes类型
    cart_bytes = base64.b64decode(cart_str_bytes)
    # 把bytes类型转换成字典
    carts_dict = pickle.loads(cart_bytes)

    # carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))



    return carts_dict