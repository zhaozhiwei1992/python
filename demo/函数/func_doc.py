#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   func_doc.py
@Time    :   2019/10/10 22:01:52
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib

#  文档字符串一定要在函数内部
#  文档字符串使用单引号双引号都可以
def echo(msg):
    '''
    我是文档字符串
    '''
    print(msg)

print(echo.__doc__)