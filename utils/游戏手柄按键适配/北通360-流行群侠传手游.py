"""
通过python + adb + scrcpy的方式，实现手柄玩安卓手机游戏

# Released by rdb under the Unlicense (unlicense.org)
# Based on information from:
# https://www.kernel.org/doc/Documentation/input/joystick-api.txt

# 参考
https://blog.csdn.net/Enderman_xiaohei/article/details/88050036?utm_medium=distribute.pc_relevant.none-task-blog-2~default~baidujs_baidulandingword~default-9-88050036-blog-109139735.pc_relevant_3mothn_strategy_recovery&spm=1001.2101.3001.4242.6&utm_relevant_index=12

https://blog.csdn.net/dhjabc_1/article/details/117444998

使用:
linux下需要使用管理员身份运行(触发按键需要), 否则运行报错

sudo python xx.py

"""
import pygame
# 键盘
import keyboard
import pyautogui
import time

# 鼠标, 没啥用了
# from pymouse import PyMouseMeta
# m = PyMouseMeta()


class JoyToKey:
    """
    将手柄映射到键盘输入上
    """

    def exec(self, joystick, event):
        #	可能的joystick行为: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        # if event.type == pygame.JOYBUTTONUP:
        #     print("Joystick button released.")
        # ********************键盘按键********************
        if event.type == pygame.KEYDOWN:
            # print(pygame.key.get_pressed())
            pass
            # event.key 表示键盘按键的值，比如k 的值是107， 回车键的值是13，等
            # self.toggle_show_fps(event.key)
        elif event.type == pygame.KEYUP:
            # print(pygame.key.get_pressed())
            pass

        # ********************手柄操作********************
        elif event.type == pygame.JOYBUTTONDOWN:
            # 检测到手柄上的键按下
            # print("Joystick button pressed.")
            if joystick.get_button(7) == 1:
                # 手柄start键 --> 键盘中的回车键。
                keyboard.press('enter')
            if joystick.get_button(0) == 1:
                # 手柄A键 --> 键盘的k键，也就是对应跳(闪)的功能。
                keyboard.press('k')
            if joystick.get_button(2) == 1:
                # 手柄X键 --> 键盘u
                keyboard.press('u')
            if joystick.get_button(1) == 1:
                # 手柄B键 --> 键盘i
                keyboard.press('i')
            if joystick.get_button(3) == 1:
                # 手柄Y键 --> 键盘p
                keyboard.press('p')
            if joystick.get_button(5) == 1:
                # 手柄又键 --> 键盘l(换武器)
                keyboard.press('l')
        elif event.type == pygame.JOYBUTTONUP:
            # print("Joystick button release.")
            if joystick.get_button(7) == 0:
                # 手柄start键 --> 键盘中的回车键。
                keyboard.release('enter')
            if joystick.get_button(0) == 0:
                # 手柄A键 --> 键盘的k键，也就是对应跳(闪)的功能。
                keyboard.release('k')
            if joystick.get_button(2) == 0:
                # 手柄X键 --> 键盘u
                keyboard.release('u')
            if joystick.get_button(1) == 0:
                # 手柄B键 --> 键盘i
                keyboard.release('i')
            if joystick.get_button(3) == 0:
                # 手柄Y键 --> 键盘p
                keyboard.release('p')
            if joystick.get_button(5) == 0:
                # 手柄又键 --> 键盘l(换武器)
                keyboard.release('l')

        # 攻击键
        elif event.type == pygame.JOYAXISMOTION:
            # print("Joystick axis pressed.")
            if joystick.get_axis(2) > 0:
                # 手柄左x --> 键盘h
                # 注意: 这里需要让手柄, pygame来控制按压和释放, 如果用pyautogui, keydown每次会触发很多按压,(连点)
                # 还是用这个保险
                keyboard.press('h')
            if joystick.get_axis(5) > 0:
                # 手柄右x --> 键盘j
                keyboard.press('j')
            if round(joystick.get_axis(1)) < 0:
                # 前
                keyboard.press('w')
            if round(joystick.get_axis(1)) > 0:
                # 后
                keyboard.press('s')
            if round(joystick.get_axis(0)) < 0:
                # 左
                keyboard.press('a')
            if round(joystick.get_axis(0)) > 0:
                # 右
                keyboard.press('d')

            # 释放
            # print("Joystick axis released.")
            # print("s", joystick.get_axis(1))
            if joystick.get_axis(2) < 0:
                # 手柄左x --> 键盘h
                keyboard.release('h')
            if joystick.get_axis(5) < 0:
                # 手柄右x --> 键盘j
                keyboard.release('j')
            if round(joystick.get_axis(0)) == 0:
                # 释放左右
                keyboard.release('a')
                keyboard.release('d')
            if round(joystick.get_axis(1)) == 0:
                # 释放前后
                keyboard.release('w')
                keyboard.release('s')

            # 摇杆转向
            # 当前鼠标光标位置, 固定位置, 不单独获取了
            # x, y = pygame.mouse.get_pos()
            x, y = 482, 305
            pyautogui.moveTo(x, y)
            # 1. 设置当前鼠标光标位置, 放中间或偏右
            # 2. 根据摇杆变化, 利用pyautogui进行拖拽
            # 3, 4为遥感的横/纵向变化
            if joystick.get_axis(3) != 0 or joystick.get_axis(4) != 0:
                # 将当前光标位置的东西向下移动100个像素点，在拖动的过程中按住鼠标左键。
                # >> > pyautogui.drag(100, 0, button='left')
                # 一样的问题, 连点
                # pyautogui.drag(int(round(joystick.get_axis(4))), int(round(joystick.get_axis(3))), button='left')
                print(y+int(round(joystick.get_axis(4))), x+int(round(joystick.get_axis(3))))

                # 使用pymouse实现上述payautogui的拖拽
                # x, y = pygame.mouse.get_pos()
                # m.press(x, y)
                # x1 = x + joystick.get_axis(3)
                # y1 = y + joystick.get_axis(4)
                # m.move(x1, y1)
                # m.release(x1, y1)


if __name__ == '__main__':
    pygame.init()

    # 初始化joystick
    pygame.joystick.init()

    # 得到joystick的数量
    joystick_count = pygame.joystick.get_count()
    print("Number of joysticks: {}".format(joystick_count))

    # 之考虑一个手柄
    joystick = pygame.joystick.Joystick(0)
    # 按键映射对象
    joyToKey = JoyToKey()

    # -------- 程序主循环 -----------
    # 保持循环直到用户点击关闭按钮
    done = False
    while not done:
        # 事件处理的步骤
        # 手柄事件触发
        for event in pygame.event.get():
            # 如果用户触发了关闭事件
            if event.type == pygame.QUIT:
                # 设置我们做了这件事的标志，所以我们就可以退出循环了
                done = True
            else:
                joyToKey.exec(joystick, event)

    # 关闭窗口并退出.
    pygame.quit()
