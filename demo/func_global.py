#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   func_global.py
@Time    :   2019/10/10 19:04:04
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib

#  全局变量
def func_global():
    global x
    print('当前x值', x)
    x = 20
x = 30
func_global()
print('执行函数后x值', x)
