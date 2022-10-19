# !user/bin/python
# _*_ coding: utf-8 _*_
#
# @Title: 根据指定前缀查找范围.py
# @Description: redis实战第6章 一个小工具测试
# @author zhaozhiwei
# @date 2022/9/30 下午5:50
# @version V1.0
import bisect


def find_prefix_range(prefix):
    """
    纯字母范围, ascii表中, 如abc 在abb{和abc{之间
    通过使用搜索如在redis或者数据库中可以找到范围内字符串组合
    """
    valid_characters = '`abcdefghigklmnopqrstuvwxyz{'
    # print(prefix[-1:])
    posn = bisect.bisect_left(valid_characters, prefix[-1:])
    suffix = valid_characters[(posn or 1) - 1]
    return prefix[:-1] + suffix + '{', prefix + '{'


if __name__ == '__main__':
    print(find_prefix_range('ab'))
