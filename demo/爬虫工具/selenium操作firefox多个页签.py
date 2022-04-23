from selenium import webdriver
import time
import pyautogui
from selenium.common.exceptions import TimeoutException

driver = webdriver.Firefox()

# 浏览器最大化
driver.maximize_window()

# 控制网站打开超时，否则get会阻塞
driver.set_page_load_timeout(1)
try:
    driver.get("https://md.phodal.com/")
except TimeoutException:
    print('timeout')
# 第二个网站
# time.sleep(2)
# 跟上述一样控制延时
# driver.implicitly_wait(2)
js = "window.open('{}','_blank');"
driver.execute_script(js.format('https://md.phodal.com/'))
driver.switch_to.window(driver.window_handles[-1])

# 回到第一个页签
# driver.switch_to.window(driver.window_handles[0])
# print(driver.window_handles)