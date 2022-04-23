#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   file_linux.py
@Time    :   2019/10/12 09:40:24
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib
import os

target_dir = '/tmp/python/'
if not os.path.exists(target_dir):
    os.mkdir(target_dir) 

target = target_dir + '11.txt'

if not os.path.exists(target):
    try:
        # 写入
        writeFile = open(target, 'a')
        writeFile.write('''
            talk is cheap, show me your code!
            all work and no play, make jack a dull boy
        ''')
    finally:
        writeFile.flush()
        writeFile.close()
    # writeFile = file(target, 'w')

try:
    # 读取数据
    readFile = open(target)
    while True:
        line = readFile.readline()
        if len(line) == 0:
            break
        else:
            print (line)
finally:
    readFile.close()