import base64
import pickle
from django_redis import get_redis_connection


def set_cart_cookie_str(carts_dict):
    """设置cart的字典转换成cookie存储的str"""

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


    return carts_dict

def merge_cart_cookie_to_redis(request, response, user):
    """
    登录后合并cookie中的购物车数据到redis中
    :param request: 本次请求对象，获取cookie中的数据
    :param response: 本次响应对象，清除cookie中的数据
    :param user: 登录用户信息，获取user_id
    :return: response
    """
    # 获取cookie中的购物车数据
    # 获取redis中的购物车数据
    # 合并购物车，以cookie中的购物车数据为准，选择按钮则以两者中有一边勾选就为勾选（这个需求后期看具体项目需求）
    # 清除cookie
    # 响应

    # 获取cookie中的购物车数据
    cookie_cart_str = request.COOKIES.get("cart")

    if not cookie_cart_str:
        return response

    cookie_cart_dict = get_cart_cookie_dict(cookie_cart_str)

    # 获取redis中的购物车数据
    redis_conn = get_redis_connection("carts")
    pl = redis_conn.pipeline()

    # 合并购物车，以cookie中的购物车数据为准，选择按钮则以两者中有一边勾选就为勾选（这个需求后期看具体项目需求）
    """
    redis
            hash：商品和数量
                键：cart_user.id
                值：{"sku_id":"count","sku_id":"count",...}
            set:勾选
                键：select_sku_id
                值：{sku_id1,sku_id2,...}
    cookie
            {
                sku_id:{count,select},
                sku_id:{count,select},
                ...
            }
    """
    # 遍历cookie购物车大字典,把sku_id及count向redis的hash中存储
    for sku_id in cookie_cart_dict:
        # 把cookie中的sku_id 和count向redis的hash去存储,如果存储的sku_id已存在,就直接覆盖,不存在就是新增
        pl.hset('cart_%d' % user.id, sku_id, cookie_cart_dict[sku_id]['count'])
        # 判断当前cookie中的商品是否勾选,如果勾选直接把勾选的商品sku_id 存储到set集合
        if cookie_cart_dict[sku_id]['selected']:
            pl.sadd('selected_%d' % user.id, sku_id)

    pl.execute()  # 执行管道
    # 清除cookie
    response.delete_cookie("cart")
    # 响应

    return response


