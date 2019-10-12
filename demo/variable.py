#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   variable.py
@Time    :   2019/10/12 22:40:42
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib

def variable(power, *args):
    '''可变参数'''
    total = 0
    for i in args:
        total += pow(i, power)
    return total

def variable2(**args):
    for i in args:
        print(i)

if __name__ == "__main__":
    print(variable(2,3,2))
    assert variable(2,3,2) == 13

    variable2(name='zhangsan', age = 18)