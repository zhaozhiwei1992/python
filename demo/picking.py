#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   picking.py
@Time    :   2019/10/12 09:59:10
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   这个玩意儿可以看做是python中对对象的序列化操作
'''

# here put the import lib
import pickle as p
import os

names = ['zhangsan', 'lisi', 'wangwu']

target_dir = '/tmp/python/'
if not os.path.exists(target_dir):
    os.mkdir(target_dir)
target = target_dir + 'dump.txt'
if not os.path.exists(target):

    '''
    TypeError: write() argument must be str, not bytes
    网上搜索才发现原来是文件打开的方式有问题。
    之前文件打开的语句是：
    f=open("list.pkl","w+")
    然后使用二进制方式打开就没有这个问题：
    f=open("list_account.pkl","wb+")
    产生问题的原因是因为pickle存储方式默认是二进制方式
    '''
    writeFile = open(target, 'wb+')
    p.dump(names, writeFile)
    writeFile.flush()
    writeFile.close()
del names
# print('删除后names的值', names)
readFile = open(target, 'rb+')
names = p.load(readFile)
print('读取序列化文件后 names 的值', names)