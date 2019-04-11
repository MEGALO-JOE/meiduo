# # import random
# #
# #
# # def rand():
# #     num = random.randint(0, 65536)
# #
# #     return num
# #
# # # 用任意数字取余数 10   0～9
# # # 65535 * 65535 % 100000000
# # # 0～5
# # #
# # # 5 * 5 % 10
# # # 0～9
# # #
# # # 【A01～A30】
# # #
# # # 0～7
# # #  6 * 6 % 10
# # #
# # #
# # # 10
# import random
#
#
# class LuckDraw:
#     """
#     使用分割存储空间 + 条件判断 减少列表迭代的时间
#     """
#     _1to65535 = []
#     _65535to65535x2 = []
#     _65535x2to65535x3 = []
#     _65535x3to65535x4 = []
#     _65535x4to300000 = []
#     __instance = None
#
#     def __iter__(self):
#         self.rand = random.randint(1,65536)
#         return self
#
#     def __next__(self):
#         if self.__get_all_length() <= 1000:
#             id_code = self.__get_id_code()
#             return id_code
#
#         else:
#             raise StopIteration("already 100000")
#
#     def __get_all_length(self):
#         """
#         或取所有结果列表的长度和
#         :return:
#         """
#         all_length = len(self._1to65535) + \
#                      len(self._65535to65535x2) + \
#                      len(self._65535x2to65535x3) + \
#                      len(self._65535x3to65535x4) + \
#                      len(self._65535x4to300000)
#         return all_length
#
#     def __get_id_code(self):
#         """
#         获取一个1-30000之内的数值，并且这个数值不与已经保存过的值重复
#         使用条件判断与结果分区保存，减少在验证重复时消耗的时间
#         :return: id_code 唯一不重复的员工ID
#         """
#         while True:
#             bet = random.randint(1, 5)
#             id_code = bet * self.rand
#             if id_code != 0:
#                 if id_code <= 65535 and id_code not in self._1to65535:
#                     self._1to65535.append(id_code)
#                     return id_code
#                 if 65535 < id_code <= 65535 * 2 and id_code not in self._65535to65535x2:
#                     self._65535to65535x2.append(id_code)
#                     return id_code
#                 if 65535 * 2 < id_code <= 65535 * 3 and id_code not in self._65535x2to65535x3:
#                     self._65535x2to65535x3.append(id_code)
#                     return id_code
#                 if 65535 * 3 < id_code <= 65535 * 4 and id_code not in self._65535x3to65535x4:
#                     self._65535x3to65535x4.append(id_code)
#                     return id_code
#                 if 65535 * 4 < id_code <= 300000 and id_code not in self._65535x4to300000:
#                     self._65535x4to300000.append(id_code)
#                     return id_code
#
#     @classmethod
#     def luck_one(cls):
#         """
#         类方法 + 单例模式 装B
#         """
#         if not cls.__instance:
#             cls.__instance = iter(cls())
#         return next(cls.__instance)
#
#
# if __name__ == '__main__':
#
#     # LuckDraw.luck_one()
#
#
#     def rand():
#         num = random.randint(0, 65536)
#
#         return num
#
#     # 30万人分5组,每组6万人
#     result = []
#
#     i = 0
#     for t in range(5):
#         # 集合不重复
#         ls = set()
#         while len(ls) != 20000:
#             num = rand()
#             # 大于6万的随机数不要,等同于random.randint(1, 60000
#             if num > 60000:
#                 continue
#             ls.add(num + 60000 * i)
#         i += 1
#         result.extend(ls)
#
#     print(result)


class A(object):

    def __init__(self):
        print("ent A")

        super(A,self).__init__()

        print("lea A")




class B(object):

    def __init__(self):
        print("ent B")

        super(B,self).__init__()

        print("lea B")
