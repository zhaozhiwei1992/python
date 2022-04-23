#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   if.py
@Time    :   2019/10/10 17:29:20
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib

number = 23
guess = int(input('enter a number'))
print('guess', guess)
if(guess > number):
    print('输入大于', number)
elif(guess < number):
    print('输入小于', number)
else:
    print('相等')
print ('Done')