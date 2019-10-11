#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   obj_method.py
@Time    :   2019/10/11 23:32:44
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def say(self, msg):
        print('say %s'%msg)

person = Person('zhangsan', 18)
person.say('hello')
print(person.age)