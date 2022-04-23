#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   function.py
@Time    :   2019/10/10 18:58:41
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib

# 函数demo
def hello(name):
    print('hello', name)

hello('world')

"""
最大数
"""
def max(a, b):
    if(a > b):
        return a
    else:
        return b
print(max(1,3))