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

        # 操作费用报销
        driver.find_element_by_xpath(
            u"(.//*[normalize-space(text()) and normalize-space(.)='费用报销'])[1]/following::*[name()='svg'][1]").click()
        driver.find_element_by_id("button-1237-btnIconEl").click()
        driver.find_element_by_xpath("//td[@id='ext-gen2638']/div").click()
        driver.find_element_by_id("ext-gen1019").click()
        driver.find_element_by_xpath("//td[@id='ext-gen3396']/div").click()
        driver.find_element_by_id("multifield-1424-inputEl").clear()
        driver.find_element_by_id("multifield-1424-inputEl").send_keys("8")
        driver.find_element_by_xpath("//td[@id='ext-gen3397']/div").click()
        # ERROR: Caught exception [ERROR: Unsupported command [doubleClick | id=multifield-1428-inputEl | ]]
        driver.find_element_by_id("multifield-1428-inputEl").clear()
        driver.find_element_by_id("multifield-1428-inputEl").send_keys("8")
        driver.find_element_by_xpath("//td[@id='ext-gen3589']/div").click()
        # ERROR: Caught exception [ERROR: Unsupported command [doubleClick | id=multifield-1432-inputEl | ]]
        driver.find_element_by_id("multifield-1432-inputEl").clear()
        driver.find_element_by_id("multifield-1432-inputEl").send_keys("8")
        driver.find_element_by_xpath("//td[@id='ext-gen3781']/div").click()
        # ERROR: Caught exception [ERROR: Unsupported command [doubleClick | id=multifield-1436-inputEl | ]]
        driver.find_element_by_id("multifield-1436-inputEl").clear()
        driver.find_element_by_id("multifield-1436-inputEl").send_keys("8")
        driver.find_element_by_xpath("//td[@id='ext-gen3973']/div").click()
        # ERROR: Caught exception [ERROR: Unsupported command [doubleClick | id=multifield-1440-inputEl | ]]
        driver.find_element_by_id("multifield-1440-inputEl").clear()
        driver.find_element_by_id("multifield-1440-inputEl").send_keys("8")
        driver.find_element_by_xpath("//td[@id='ext-gen4165']/div").click()
        # ERROR: Caught exception [ERROR: Unsupported command [doubleClick | id=multifield-1444-inputEl | ]]
        driver.find_element_by_id("multifield-1444-inputEl").clear()
        driver.find_element_by_id("multifield-1444-inputEl").send_keys("8")
        driver.find_element_by_id("gridview-1305").click()
        driver.find_element_by_id("button-1344-btnIconEl").click()
        driver.find_element_by_id("tool-1351-toolEl").click()

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
