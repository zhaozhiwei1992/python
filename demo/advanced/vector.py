#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   vector.py
@Time    :   2019/10/14 19:26:50
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib
from math import hypot

class Vector:
    '''
    向量表示
    '''

    def  __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __repr__(self):
        '''
        标识对象输出的字符串形式
        默认: <__main__.Vector object at 0x7f9f5456b710>
        交互式控制台和调试程序（debugger）用 repr 函数来获取字符串表示
        形式；在老的使用 % 符号的字符串格式中，这个函数返回的结果用来代
        替 %r 所代表的对象；

        '''
        return 'Vector(%r, %r)' %(self.x, self.y)

    def __abs__(self):
        return hypot(self.x, self.y)

    def __bool__(self):
        return bool(self.x or self.y)
    
    def __add__(self, other):
        '''
        >>> v1 = Vector(1, 2)
        >>> v2 = Vector(4, 6)
        Vector(5, 8)
        '''
        x = self.x + other.x
        y = self.y + other.y
        return Vector(x, y)

    def __mul__(self, salary):
        '''
        >>> v = Vector(1, 2)
        >>> v * 3
        Vector(3, 6)
        '''
        return Vector(self.x * salary, self.y * salary)

if __name__ == "__main__":
    vec = Vector(1, 2)
    # print(vec)
    vec2 = Vector(3, 4)
    print(vec + vec2)
    print(vec * 3)