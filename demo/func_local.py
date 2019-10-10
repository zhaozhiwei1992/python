#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   func_local.py
@Time    :   2019/10/10 19:08:49
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib

def func_local(x):
    print('当前值', x)
    x = 20
x = 30
func_local(x)
print('执行函数后值不变:', x)