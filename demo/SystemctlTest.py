"""

[Unit]
Description=auth by face

[Service]
Type=simple
ExecStart=/usr/bin/python /home/zhaozhiwei/workspace/python/demo/SystemctlTest.py
#ExecStart=/bin/sh -c "/usr/bin/python /home/zhaozhiwei/workspace/python/demo/SystemctlTest.py"

[Install]
WantedBy=multi-user.target

1. 在/usr/lib/systemd/system/下创建systemctl-test.service
2. systemctl start systemctl-test.service即可
3. 查看启动状态 systemctl status systemctl-test.service

"""
import os
import time

if __name__ == '__main__':
    while True:
        time.sleep(20)
        print("hh")
