#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   tuple_print.py
@Time    :   2019/10/10 22:52:40
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib

numbers = tuple(range(1, 5))
print(numbers)

name = 'zhangsan'
age = 18
#  注意这里%之前不能有 逗号
print('name is %s, age is %d' %(name, age))