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

#
# class A(object):
#
#     def __init__(self):
#         print("ent A")
#
#         super(A,self).__init__()
#
#         print("lea A")
#
#
#
#
# class B(object):
#
#     def __init__(self):
#         print("ent B")
#
#         super(B,self).__init__()
#
#         print("lea B")
#
#
# # for sku_id_bytes, count_bytes in cart_redis_dict.items():  # 遍历hash中的所有键值对字典,
# #     cart_dict[int(sku_id_bytes)] = {  # 包到字典中的数据注意类型转换
# #         'count': int(count_bytes),
# #         'selected': sku_id_bytes in selecteds
# #     }
#
# a = {1:"nihao",2:"buhao"}
#
# print(a.items())
#
# aa = []
# bb = []
#
# for key,value in a.items():
#     aa.append(key)
#     bb.append(value)
#
#
# print(aa)
# print(bb)



# 冒泡排序：
def bubble_sort(alist):
    """冒泡排序"""

    for j in range(len(alist)-1,0,-1):
        for i in range(j):
            # if  alist[i] > alist[i+1]:
            if alist[i] < alist[i+1]:
                alist[i], alist[i+1] = alist[i+1],alist[i]



def quick_sort(alist,start,end):
    """快速排序"""


    # 设置哨兵
    # 左变哨兵
    left = start
    # 右边哨兵
    right = end

    # 基数
    mid = alist[left]

    if left >= right:
        return alist

    while left < right:

        # 如果 right 与 left 未重合，left 指向的元素不比基准元素小，则 left 向左移动
        while (left < right) and (alist[right] >= mid):
            right -= 1

        alist[left] = alist[right]

        while (left < right) and (alist[left] <= mid):
            left += 1

        alist[right] = alist[left]

    # 退出循环后，right与left重合
    alist[left] = mid

    # 对基准左边的进行快速排序
    quick_sort(alist,start,left-1)

    # 对基准的右边进行快速排序
    quick_sort(alist,right+1,end)

    return alist

#QuickSort by Alvin

def QuickSort(myList,start,end):
    #判断low是否小于high,如果为false,直接返回
    if start < end:
        i,j = start,end
        #设置基准数
        base = myList[i]

        while i < j:
            #如果列表后边的数,比基准数大或相等,则前移一位直到有比基准数小的数出现
            while (i < j) and (myList[j] >= base):
                j = j - 1

            #如找到,则把第j个元素赋值给第个元素i,此时表中i,j个元素相等
            myList[i] = myList[j]

            #同样的方式比较前半区
            while (i < j) and (myList[i] <= base):
                i = i + 1
            myList[j] = myList[i]
        #做完第一轮比较之后,列表被分成了两个半区,并且i=j,需要将这个数设置回base
        myList[i] = base

        #递归前后半区
        QuickSort(myList, start, i - 1)
        QuickSort(myList, j + 1, end)
    return myList

#
# myList = [49,38,65,97,76,13,27,49]
# print("Quick Sort: ")
# QuickSort(myList,0,len(myList)-1)
# print(myList)
#

list = [54,23,77,1,34,97,3,36]

# bubble_sort(list)
quick_sort(list,0,len(list)-1)

print(list)



a = "a",
b = "b",

c,d = a,b

print(c)
print(d)

