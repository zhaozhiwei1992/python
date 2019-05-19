# -*- coding:utf-8 -*-

"""
不改变原顺序去重
如果可以改变直接set(list)
"""
# def dedupe(items):
#     seen=set()
#     for item in items:
#         if item not in seen:
#             yield item
#             seen.add(item)

"""
进阶版，支持对象去重
"""
def dedupe(items, key=None):
    seen=set()
    for item in items:
        val = item if key is None else key(item)
        if val not in seen:
            yield item
            seen.add(item)


if __name__ == "__main__":
    a=[1,2,3,2,4,5,1,6,7]
    print(list(dedupe(a)))

    # users=[
    #     {'name':'zhangsan', 'age':18},
    #     {'name':'lisi', 'age':16},
    #     {'name':'wangwu', 'age':14},
    #     {'name':'lisi', 'age':13},
    #     {'name':'wangwu', 'age':10}
    # ]
    ages=[
        {'x':18},
        {'x':16},
        {'x':14},
        {'x':13},
        {'x':10}
    ]
    print(list(dedupe(ages, key=lambda d:d['x'])))