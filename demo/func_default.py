#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   func_default.py
@Time    :   2019/10/10 19:12:23
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib
def hello(message = 'world'):
    print('hello', message)

hello()
hello('bob')