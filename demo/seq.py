#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   seq.py
@Time    :   2019/10/10 23:12:14
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib

animal=["cat", "dog", "pig"]
animal.append("eleph")
print('all animal', animal)
# 切片包括前数不包括后数
print('0::2', animal[0:2])
print('0::-1', animal[0::-1])
print('0:-1', animal[0:-1])
print('-2::-1', animal[-2:-1])
print('::2', animal[::2])