#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   comprehension.py
@Time    :   2019/10/14 22:40:06
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   列表生成器和传统语法
'''

# here put the import lib

if __name__ == "__main__":
    symbols = '$¢£¥€¤'
    # 使用传统语法转成对应ascii
    symbolsAscii = list(filter(lambda c: c >127, map(ord, symbols)))
    print('传统方法构建list', symbolsAscii)
    # 使用推导式转成对应ascii
    symbolsAscii = [ord(i) for i in symbols if ord(i) > 127]
    print('列表推到式', symbolsAscii)