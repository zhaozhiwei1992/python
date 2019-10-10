#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   using_sys.py
@Time    :   2019/10/10 22:09:16
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib
import sys

'''
python using_sys.py xx1 xx2 xx3
'''
print('命令参数')
for i in sys.argv:
    print(i)

print('python path', sys.path)