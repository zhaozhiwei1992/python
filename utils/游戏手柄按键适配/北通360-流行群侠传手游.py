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
import keyboard
import pyautogui
import configparser
import time


class JoyToKeyMouse:
    def __init__(self, key_mapping, mouse_speed):
        self.key_mapping = key_mapping
        self.mouse_speed = mouse_speed
        self.last_joystick_event_time = 0
        self.joystick_event_interval = 0.1  # 设置摇杆事件的间隔阈值
        self.joystick_release_threshold = 0.2  # 设置摇杆释放的阈值,解决释放后还连续触发

        # 初始化pygame
        pygame.init()
        pygame.joystick.init()

        # 初始化手柄
        joystick_count = pygame.joystick.get_count()
        print("Number of joysticks: {}".format(joystick_count))
        if joystick_count < 1:
            raise RuntimeError("No joystick detected.")
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        # 初始化屏幕
        # self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        # pygame.display.set_caption("JoyToKeyMouse")

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.JOYBUTTONDOWN:
            button = str(event.button)
            if button in self.key_mapping:
                print("按钮 {}, 映射 {}".format(button, self.key_mapping[button]))
                keyboard.press(self.key_mapping[button])
        elif event.type == pygame.JOYBUTTONUP:
            button = str(event.button)
            if button in self.key_mapping:
                print("按钮 {}, 映射 {}".format(button, self.key_mapping[button]))
                keyboard.release(self.key_mapping[button])
        elif event.type == pygame.JOYAXISMOTION:
            axis = event.axis
            value = event.value
            # 计算时间间隔
            current_time = time.time()
            time_diff = current_time - self.last_joystick_event_time

            # 如果事件间隔小于阈值，则忽略此次摇杆事件
            if time_diff < self.joystick_event_interval:
                return False
            if str(axis) in self.key_mapping:
                print('摇杆有毛个映射,别瞎写')
                # if value > 0:
                #     keyboard.press(self.key_mapping[axis])
                # else:
                #     keyboard.release(self.key_mapping[axis])
            if axis == 0 or axis == 1:
                # 获取左摇杆的坐标
                left_stick_x = self.joystick.get_axis(0)
                left_stick_y = self.joystick.get_axis(1)

                # 计算鼠标的移动增量
                mouse_dx = left_stick_x * self.mouse_speed
                mouse_dy = left_stick_y * self.mouse_speed

                # 获取当前鼠标位置
                mouse_x, mouse_y = pyautogui.position()

                # 计算新的鼠标位置
                new_mouse_x = max(0, min(pyautogui.size()[0], mouse_x + mouse_dx))
                new_mouse_y = max(0, min(pyautogui.size()[1], mouse_y + mouse_dy))

                # 右摇杆X轴方向
                if value > 0:
                    # 模拟鼠标左键按下
                    pyautogui.mouseDown(button='left')
                else:
                    # 模拟鼠标左键释放
                    pyautogui.mouseUp(button='left')
                # 移动鼠标
                pyautogui.moveTo(new_mouse_x, new_mouse_y)
            # 更新上一次摇杆事件处理时间戳
            self.last_joystick_event_time = current_time
            if abs(self.joystick.get_axis(0)) < self.joystick_release_threshold and abs(
                    self.joystick.get_axis(1)) < self.joystick_release_threshold:
                # 摇杆已经释放，重置上次摇杆事件处理时间戳
                self.last_joystick_event_time = 0
        elif event.type == pygame.JOYHATMOTION:
            hat_x, hat_y = event.value
            if hat_x == -1:
                print('向左移动')
                keyboard.press(self.key_mapping['LEFT'])
            elif hat_x == 1:
                print('向右移动')
                keyboard.press(self.key_mapping['RIGHT'])
            else:
                keyboard.release(self.key_mapping['LEFT'])
                keyboard.release(self.key_mapping['RIGHT'])
            if hat_y == -1:
                print('向后移动')
                keyboard.press(self.key_mapping['DOWN'])
            elif hat_y == 1:
                print('向前移动')
                keyboard.press(self.key_mapping['UP'])
            else:
                keyboard.release(self.key_mapping['UP'])
                keyboard.release(self.key_mapping['DOWN'])
        return False


def load_key_mapping(mapping_file):
    key_mapping = {}
    with open(mapping_file, 'r') as file:
        for line in file:
            button, key = line.strip().split(',')
            # key要去掉注释部分
            key_mapping[button] = key.split('#')[0].strip()
    return key_mapping


def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    mouse_speed = int(config['MOUSE']['speed'])
    return mouse_speed


def main():
    key_mapping = load_key_mapping('/home/zhaozhiwei/workspace/python/utils/游戏手柄按键适配/key_mapping.txt')
    mouse_speed = load_config('/home/zhaozhiwei/workspace/python/utils/游戏手柄按键适配/config.ini')
    joy_to_key_mouse = JoyToKeyMouse(key_mapping, mouse_speed)

    done = False
    while not done:
        for event in pygame.event.get():
            done = joy_to_key_mouse.handle_event(event)

    pygame.quit()


if __name__ == '__main__':
    main()
