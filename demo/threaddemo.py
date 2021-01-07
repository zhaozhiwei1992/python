#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import _thread as thread
import time
import datetime

import requests
import json

import random
 
def GET(url):
    #get请求
    req = requests.get(url)
    #输出状态码
    print(req.status_code)
    #输出返回内容
    print(req.text)
 
def run( threadName, delay):

    # 数据个数就是请求次数
    # 记录所有请求耗时
    times=[]
    print ("当前线程: %s: 启动, 时间%s" % ( threadName, time.ctime(time.time()) ))
    # 持续请求网站600秒
    starttime = datetime.datetime.now()

    print("启动时间 %s 当前时间 %s\n"%(starttime, starttime))
    while True:

        methodStarttime = datetime.datetime.now()

        # 请求并记录
        # resp = requests.get("obs.cstcloud.cn")
        time.sleep(random.randint(1, 2))
        # 获取返回结果

        methodEndtime = datetime.datetime.now()
        times.append((methodEndtime - methodStarttime).seconds)

        now = datetime.datetime.now()
        if((now - starttime).seconds > delay):
            break
        # print("启动时间 %s 当前时间 %s"%(starttime, now))
    # print("线程: %s结束"%(threadName))
    # 循环外持久化
    print("线程: %s 接口访问情况 %s\n"%(threadName, times))
 
# 创建两个线程
try:
    for i in range(3):
        thread.start_new_thread( run, ("Thread-%s"%(i), 20) )
except:
   print ("Error: unable to start thread")
 
#  避免窗口关闭
while 1:
   pass
