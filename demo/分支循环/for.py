#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   for.py
@Time    :   2019/10/10 18:46:46
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

"""
默认地，range的步长为1。如果我们为range提供第
三个数，那么它将成为步长。例如，range(1,5,2)给出[1,3]。记住，range 向上 延伸到第二个
数，即它不包含第二个数。

"""
step = 2
# here put the import lib
for i in range(1, 5, step):
    print("当前位置", i)
else:
    print('done .')

# range(1,5) == [1, 2, 3, 4]
for i in [1, 2, 3, 4]:
    if(i % step == 0):
        continue
    print("当前位置", i)
else:
    print('done .')