import time
from urllib import parse
import schedule
import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By

# 配置文件路径
CONFIG_FILE = 'config.ini'


def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config


def setup_chrome_options(download_dir):
    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': download_dir,
             "download.prompt_for_download": False,
             "download.directory_upgrade": True,
             "safebrowsing.enabled": True}
    chrome_options.add_experimental_option('prefs', prefs)
    # chrome_options.add_argument('--headless')  # 无头模式
    # chrome_options.add_argument('--no-sandbox')  # 解决DevToolsActivePort文件不存在的报错
    # chrome_options.add_argument('--disable-dev-shm-usage')  # 解决内存不足的问题
    # chrome_options.add_argument("--window-size=1920,1080") # 解决设置成无头模式就报错,设置固定分辨率
    return chrome_options


def login_and_get_token(driver, login_url, username, password):
    driver.get(login_url)

    # 跳转普通登录
    login_simple = driver.find_element(By.CLASS_NAME, 'normalLogin')
    login_simple.click()
    time.sleep(1)

    # 输入用户名和密码进行登录
    username_field = driver.find_element(By.NAME, 'userName')
    password_field = driver.find_element(By.NAME, 'password')
    login_button = driver.find_element(By.CLASS_NAME, 'upbtn')

    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()

    # 等待页面加载和重定向
    time.sleep(5)

    # 切换页签
    driver.switch_to.window(driver.window_handles[0])
    print(driver.current_url)

    # 获取token
    url = parse.urlparse(driver.current_url)
    token = parse.parse_qs(url.query).get('tokenid')[0]
    print(token)
    return token


def download_file(export_url, token, chrome_options, chromedriver_path, download_dir):
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)

    try:
        driver.get(export_url.replace('#tokenid', token))
        # 获取所有按钮
        allSpan = driver.find_element_by_class_name('boxOperList').find_elements_by_tag_name('span')
        # 根据描述获取导出按钮   报表导出
        for spanItem in allSpan:
            if spanItem.text == '报表导出':
                spanItem.click()

        # 等待文件下载完成
        time.sleep(2)
        # 点击确认按钮, 这里不同的浏览器可能得单独调试
        driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[2]/div/div/a[2]/span/span/span[2]').click()
        time.sleep(10)
    finally:
        driver.quit()

    print(f'文件已保存到 {download_dir}')


def job(config):
    login_url = config['settings']['LOGIN_URL']
    username = config['settings']['USERNAME']
    password = config['settings']['PASSWORD']
    chromedriver_path = config['settings']['CHROMEDRIVER_PATH']
    download_dir = config['settings']['DOWNLOAD_DIR']
    export_urls = config['urls']['EXPORT_URLS'].split(',')

    chrome_options = setup_chrome_options(download_dir)
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)

    try:
        token = login_and_get_token(driver, login_url, username, password)
        for export_url in export_urls:
            download_file(export_url, token, chrome_options, chromedriver_path, download_dir)
    finally:
        driver.quit()


def main():
    config = load_config()
    schedule_time = config['schedule']['TIME']
    # 定时执行
    # schedule.every().day.at(schedule_time).do(job, config)
    #
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    # 临时测试
    job(config)


if __name__ == '__main__':
    main()
