#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   tshirts.py
@Time    :   2019/10/14 22:47:13
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib

colors = ['black', 'write']
sizes = ['S', 'M', 'L']
tshirts = [(color, size) for color in colors
                                    for size in sizes]
print('tshirt组合' , tshirts)

'''
生成器表达式　性能更优
生成器表达式的语法跟列表推导差不多，只不过把方括号换成圆括号而
已。

'''
for tshirt in tuple('%s, %s'%(color, size) for color in colors
            for size in sizes):
                print(tshirt)