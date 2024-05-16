import time
from urllib import parse

from selenium import webdriver
from selenium.webdriver.common.by import By

# 配置
LOGIN_URL = 'http://192.168.22.122:8001/uportal/login'
EXPORT_URL = 'http://192.168.22.122:8001/pay/commonmanagerequest/audit.page?mouldid=2395F892FE0FB5723E07BCE9DBC1B761&vchtypeid=D8B9A1F343F5A192B4C558976559E12A&mainmenu=pay0000&submenu=25377D85328251CB5A90C219D3272ADD&appid=pay&year=2024&tokenid=#tokenid&menuId=25377D85328251CB5A90C219D3272ADD&menuName=%E5%8D%95%E4%BD%8D%E5%AE%A1%E6%A0%B8&theme=default'
DOWNLOAD_DIR = '/tmp'
USERNAME = '3400_admin'
PASSWORD = '1Qa1234567890'

# 设置Chrome选项
chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory': DOWNLOAD_DIR,
         "download.prompt_for_download": False,
         "download.directory_upgrade": True,
         "safebrowsing.enabled": True
         }
chrome_options.add_experimental_option('prefs', prefs)

# 使用webdriver_manager自动下载和安装ChromeDriver
driver = webdriver.Chrome(executable_path='/tmp/chromedriver-linux64/chromedriver', options=chrome_options)

try:
    # 打开登录页面
    driver.get(LOGIN_URL)

    # 跳转普通登录
    login_simple = driver.find_element_by_class_name('normalLogin')
    login_simple.click()
    time.sleep(1)

    # 输入用户名和密码进行登录
    username_field = driver.find_element(By.NAME, 'userName')
    password_field = driver.find_element(By.NAME, 'password')
    login_button = driver.find_element_by_class_name('upbtn')

    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)
    login_button.click()

    # 等待页面加载和重定向
    time.sleep(5)

    # 切换页签，否则无法获取当前跳转后url,  https://blog.csdn.net/weixin_44623675/article/details/86662462
    driver.switch_to.window(driver.window_handles[0])
    print(driver.current_url)
    # 获取token（如果需要）
    url = parse.urlparse(driver.current_url)
    token = parse.parse_qs(url.query).get('tokenid')[0]
    print(token)

    # 导出文件,
    # 1. 替换url中tokenid部分
    driver.get(EXPORT_URL.replace('#tokenid', token))
    tab = driver.find_element_by_xpath('/html/body/div[2]/div[3]/ul/li[4]')
    tab.click()
    time.sleep(1)  # 根据实际情况调整等待时间
    export_button = driver.find_element(By.ID, '导出')
    export_button.click()
    # time.sleep(5)  # 根据实际情况调整等待时间
    # confirm = driver.find_element_by_xpath('/html/body/div[8]/div[3]/button[1]')
    # confirm.click()
    # 等待文件下载完成
    time.sleep(10)  # 根据实际情况调整等待时间

finally:
    # 关闭浏览器
    driver.quit()

print(f'文件已保存到 {DOWNLOAD_DIR}')
