#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   backup.py
@Time    :   2019/10/11 22:34:56
@Author  :   p205
@Version :   1.0
@Contact :   zhaozhiweishanxi@gmail.com
@License :   (C)Copyright 2019-2020, p205
@Desc    :   None
'''

# here put the import lib
import os
import time

'''
备份指定文件
'''
def backup():
    '''
    备份目录下所有文件，并根据时间区分
    '''
    source = ['~/Documents/notes']
    target_dir = '/tmp/'
    # 日期当做目录
    today = target_dir + time.strftime('%Y%m%d')
    if not os.path.exists(today) :
        os.mkdir(today)
        print('success create dir %s' %today)
    # 当前时间,精确到秒
    now = time.strftime('%H%M%S')

    # os.seq 按系统区分的分隔符
    target = today + os.sep + now + '.tar.gz'

    command = 'tar -zcvf %s %s' %(target, ' '.join(source))

    if os.system(command) == 0:
        print("successful backup to %s" %target)
    else:
        print("backup fail")

if __name__ == "__main__":
    backup()