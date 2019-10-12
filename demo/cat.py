#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   cat.py
@Time    :   2019/10/12 22:15:31
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib
import sys
import os

'''
通过python实现一个简单的cat命令
cat xx, 输出文件内容
cat --version 输出版本
cat --help 输出帮助信息

测试: python cat.py cat.py 输出cat.py中内容
'''

def readFile(name):
    if os.path.exists(name):
        f = open(name, 'r+')
        while(True):
            line = f.readline()
            if(len(line) == 0):
                break
            else:
                print(line)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("No action input")
        sys.exit()

    #  如果--开头标识参数
    if sys.argv[1].startswith('--'):
        option = sys.argv[1][2:]
        if 'version' == option:
            print('''
            cat (GNU coreutils) 8.31
            Copyright (C) 2019 Free Software Foundation, Inc.
            许可证 GPLv3+：GNU 通用公共许可证第 3 版或更新版本<https://gnu.org/licenses/gpl.html>。
            本软件是自由软件：您可以自由修改和重新发布它。
            在法律范围内没有其他保证。

            由Torbjorn Granlund 和Richard M. Stallman 编写
            ''')
        elif 'help' == option:
            print('I will help you')
        else:
            print('敬请期待')
    else:
        readFile(sys.argv[0])
