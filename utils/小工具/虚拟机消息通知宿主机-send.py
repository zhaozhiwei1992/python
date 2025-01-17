#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
1. 解决虚拟机中企业微信有消息时, 宿主机接收不到
"""

import pygetwindow as gw
import time
import socket

HOST = '10.0.2.15'#宿主机IP地址
PORT = 7777

# 1. 监听企业微信收到消息: 屏幕闪烁, 网络拦截?
def weixin_work_active():
    prev_window_title = None

    while True:
        # 获取当前活动窗口
        active_window = gw.getActiveWindow()
        if active_window:
            window_title = active_window.title
            # 检查窗口标题是否包含企业微信未读消息标识
            if "企业微信" in window_title and "未读消息" in window_title:
                # 如果窗口标题发生变化，发送通知到宿主机
                if window_title != prev_window_title:
                    send_message()
                    prev_window_title = window_title
            else:
                prev_window_title = None
        time.sleep(1)  # 每隔1秒检查一次

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