#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 文件名：socket客户端.py

import socket  # 导入 socket 模块

s = socket.socket()  # 创建 socket 对象
host = socket.gethostname()  # 获取本地主机名
port = 12345  # 设置端口号

s.connect((host, port))
print(str(s.recv(1024), encoding='utf-8'))
s.close()