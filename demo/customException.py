#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   customException.py
@Time    :   2019/10/12 21:47:39
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib

class InputShortException(Exception):
    '''自定义异常'''
    def __init__(self, length, atleast):
        Exception.__init__(self)
        self.length = length
        self.atleast = atleast

if __name__ == "__main__":
    inputString = input('请输入字符串: ')
    atleast = 5
    try:
        if len(inputString) < atleast:
            raise InputShortException(len(inputString), atleast)
    except EOFError:
        print('please dont input EOF only')
    except InputShortException as x:
        print('InputShortException length is %d, atleast %d' %(x.length, x.atleast))
    else:
        print("done")