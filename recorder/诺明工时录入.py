# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re


class AppDynamicsJob(unittest.TestCase):
    def setUp(self):
        # AppDynamics will automatically override this web driver
        # as documented in https://docs.appdynamics.com/display/PRO44/Write+Your+First+Script
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def test_app_dynamics_job(self):
        driver = self.driver
        # 登录
        driver.get("http://www.tjhqpm.cn:8088/ess/framework/login")
        driver.find_element_by_id("userid").clear()
        driver.find_element_by_id("userid").send_keys("LT1336")
        driver.find_element_by_id("userpwd").clear()
        driver.find_element_by_id("userpwd").send_keys("LT1336")
        driver.find_element_by_id("bLogin").click()

        time.sleep(1)  # sleep for 1 sec
        # 操作 工时填报, 定位是费用报销 日..
        driver.find_element_by_xpath(
            u"(.//*[normalize-space(text()) and normalize-space(.)='费用报销'])[1]/following::*[name()='svg'][1]").click()

        time.sleep(1)  # sleep for 1 sec
        # 新建
        driver.find_element_by_id("button-1028-btnIconEl").click()

        # 录入表单, 13列 第一行
        # document.getElementsByClassName('x-grid-row x-grid-row-selected x-grid-data-row x-grid-row-focused')[1].childNodes
        # 每一个td里, 第一个div的text设置值即可
        # todo 遍历节点赋值
        # 1. 如何遍历节点
        # 2. 如何找子节点 by_xpath
        tr = driver.find_element_by_xpath('//*[@id="gridview-1097-record-ext-record-1426"]')
        tds = tr.find_elements_by_tag_name('td')
        for index, td in enumerate(tds):
            print(index, td)
            div = td.find_element_by_tag_name('div')
            # 录五天比较保险, 直接给div设置参数不可行, 还是需要点击，录入模拟操作
            if(index == 1):
                # driver.find_element_by_xpath("//td[@id='ext-gen1991']/div").click()
                # driver.find_element_by_xpath("//td[@id='ext-gen2118']/div").click()
                # todo 需要模拟点击
                driver.execute_script("arguments[0].innerHTML = '[RX202010058-TF202012474]浙江省数字财政管理中心金财2.0业务中台适配改造及实施项目';", div)
            elif(index == 2):
                driver.execute_script("arguments[0].innerHTML = '[WBS-KF]财政研发中心';", div)
            elif(index == 3):
                driver.execute_script("arguments[0].innerHTML = '[KF-SX]开发与测试任务';", div)
            if(index > 5 and index < 11):
                # arguments[0]对应的是第一个参数，可以理解为python里的%s传参，与之类似
                # driver.execute_script("arguments[0].innerHTML = '8';", div)
               div.click()
               # div.find_element_by_tag_name('input').clear()
               # div.find_element_by_tag_name('input').send_keys("8")
               # //*[@id="multifield-1218-inputEl"]
               #  属性找的不够准确, 根据显示的ext-comp, display <> none的,里边找input
               driver.find_element_by_xpath("//input[contains(@id,'-inputEl')]").clear()
               driver.find_element_by_xpath("//input[contains(@id,'-inputEl')]").send_keys("8")
               # driver.find_element_by_id("multifield-.*-inputEl").clear()
               # driver.find_element_by_id("multifield-.*-inputEl").send_keys("8")

        # todo 退处界面
        # todo 退出登录
        # driver.find_element_by_id("gridview-1305").click()
        # driver.find_element_by_id("button-1344-btnIconEl").click()
        # driver.find_element_by_id("tool-1351-toolEl").click()

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        # To know more about the difference between verify and assert,
        # visit https://www.seleniumhq.org/docs/06_test_design_considerations.jsp#validating-results
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
