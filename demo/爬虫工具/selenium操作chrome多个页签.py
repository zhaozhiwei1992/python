from selenium import webdriver
import time
import pyautogui
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()                  # 创建一个配置对象

# options.add_argument('--headless')                 # 开启无界面模式
options.add_argument("--disable-gpu")              # 禁用gpu
# options.add_argument('--user-agent=Mozilla/5.0 HAHA')  # 配置对象添加替换User-Agent的命令
# options.add_argument('--window-size=1366,768')    # 设置浏览器分辨率（窗口大小）
options.add_argument('--start-maximized')         # 最大化运行（全屏窗口）,不设置，取元素会报错
# options.add_argument('--disable-infobars')        # 禁用浏览器正在被自动化程序控制的提示
# options.add_argument('--incognito')               # 隐身模式（无痕模式）
# options.add_argument('--disable-javascript')      # 禁用javascript
driver = webdriver.Chrome(chrome_options=options)
# 浏览器最大化并打开百度
driver.maximize_window()
# 控制网站打开超时，否则get会阻塞
driver.set_page_load_timeout(1)
try:
    driver.get("https://www.jianshu.com/")
except TimeoutException:
    print('timeout')
# 第二个网站
# 获取当前窗口句柄
main_window = driver.current_window_handle
# time.sleep(2)

# 执行 JavaScript 打开新标签页
driver.execute_script("window.open('');")
# 切换到新标签页
new_window = [window for window in driver.window_handles if window != main_window][0]
driver.switch_to.window(new_window)
# 在新标签页中加载指定 URL
driver.set_page_load_timeout(2)  # 增加页面加载超时时间为10秒
try:
    driver.get("https://md.phodal.com/")
except TimeoutException:
    print('timeout')

# 获取界面一些操作
content_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="input"]'))
)
content_input.clear()
content_input.send_keys('# hello world')

# 点击复制

# 获取结果
# content_output = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '//*[@id="output"]'))
# )
# print(content_output.text)

# 回到最开始页签
driver.switch_to.window(main_window)
