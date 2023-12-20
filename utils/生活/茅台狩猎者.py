# !user/bin/python
# _*_ coding: utf-8 _*_
#
# @Title: 茅台狩猎者.py
# @Description: 通过脚本每天定点执行，
# 通过连接手机adb代替人工操作
# @author zhaozhiwei
# @date 2022/9/18 下午5:03
# @version V1.0

import os
import time


def jd_show():
    """
    打开app, 不然容易忘
    """
    # 1. 启动京东app
    os.system("adb shell am start -n com.jingdong.app.mall/.main.MainActivity")
    # 留点时间给程序反应
    time.sleep(10)

    # 如果是9点59-11点59分内预约

    # 定位搜索, 并输入关键字 "茅台飞天 53度" 确定
    os.system("adb shell input tap 266 207")
    time.sleep(10)

    os.system("adb shell input text '53\\ 500ml'")
    time.sleep(10)

    # 选中搜索结果
    os.system("adb shell input tap 235 229")
    time.sleep(10)

    # 选中预约对象, 飞天茅台 500ml
    os.system("adb shell input tap 510 845")
    time.sleep(19)

    # 十点一到, 两分钟内一顿狂点
    while True:
        os.system("adb shell input tap 848 1761")
        time.sleep(0.1)

    # print("预约成功")

    # 12点-12点05进行抢购


if __name__ == '__main__':
    """
    1. 京东-10点预约-12点开抢
2. 苏宁易购-前一天晚上9点预约-第二天下午8点开抢
3. 淘宝-晚上8点开抢
4. 网易严选-上午11点和晚上8点开抢
5. 小米有品-上午10点30预约-第二天10点开抢
    """
    # 京东抢购茅台
    jd_show()
