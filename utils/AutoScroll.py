"""
看pdf时候，让其自动滚动
1. 根据参数调整滚动速度
2. 根据快捷键停止运行
3. 快捷键启动
"""

import pyautogui
import time

if __name__ == '__main__':
    # 按照指定的频率翻页, 暂定2秒滚动3行
    while True:
        print("hello world")
        pyautogui.scroll(-3)
        time.sleep(2)