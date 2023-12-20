# !user/bin/python
# _*_ coding: utf-8 _*_
#
# @Title: 工作虽好不要贪杯哦.py
# @Description: 设置工作时间和休息时间, 到时自动黑屏并且不支持解锁
# 每45分钟休息十分钟
# @author zhaozhiwei
# @date 2022/10/24 下午7:17
# @version V1.0

import time
import os
import platform

work_time = 45
break_time = 10
break_time = break_time*60
os_str = platform.system()
work_stage = 0
while True:
    for i in range(work_time):
        print('Remain ', work_time-i, 'min')
        time.sleep(60)

    # During the break time
    # the display should always be closed
    # if rewake by mouse, it will be closed again
    inSleep = 1
    start_time = time.time()
    while inSleep:
        if os_str == "Windows":
            # Under windows, nircmd should be installed first
            # The usage can reference: www.nirsoft.net/utils/nircmd.html
            os.system("nircmd.exe monitor off")
        elif os_str == "Linux":
            os.system("xset dpms force off")
        end_time = time.time()
        if end_time-start_time > break_time:
            inSleep = 0

    if os_str == "Linux":
        os.system("xset dpms force on")
    elif os_str == "Windows":
        os.system("nircmd.exe monitor on")