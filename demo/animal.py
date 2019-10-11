#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   animal.py
@Time    :   2019/10/11 23:47:50
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib

class Animal:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def toString(self):
        print('%s name is %s age is %d'%(self, self.name, self.age))

class Dog(Animal):
    ''' dog class'''
    def __init__(self, name, age, skr):
        Animal.__init__(self, name, age)
        self.skr = skr

class Pig(Animal):
    def toString(self):
        print('%s name is %s age is %d'%(self, self.name, self.age))

if __name__ == "__main__":
    dog = Dog('bb', 3, 'eat')
    dog.toString()

    pig = Pig('pp',6)
    pig.toString()