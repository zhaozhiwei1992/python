#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
1. 解决虚拟机中企业微信有消息时, 宿主机接收不到
"""

import socket

HOST = '192.168.0.126'#宿主机IP地址
PORT = 8001

# 1. 监听企业微信收到消息: 屏幕闪烁, 网络拦截?
def weixin_work_active():
    pass

# 2. 通过socket等通信方式传递宿主机
# 3. 宿主机监听到后，弹出提示或者直接跳转虚拟机并打开企业微信

def send_message(): # 通知宿主机
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.send('new_msg')
    data = s.recv(10)
    print(data)

if __name__ == '__main__':
    weixin_work_active()
    send_message()