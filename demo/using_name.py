#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   using_name.py
@Time    :   2019/10/10 22:19:22
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib

'''
➜  demo git:(master) ✗ python using_name.py           
using by myself
➜  demo git:(master) ✗ python              
Python 3.7.4 (default, Oct  4 2019, 06:57:26) 
[GCC 9.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import using_name
using by others 
'''
if __name__ == "__main__":
    print("using by myself")
else:
    print('using by others ')