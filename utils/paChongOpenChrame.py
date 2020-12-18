# -- coding: utf-8 --
#导入selenium下的webdriver
import time
import os 
from selenium import webdriver

if os.path.exists("test.txt"):
    os.remove("test.txt")
file_obj =open("test.txt",'w')

#创建一个谷歌浏览器
driver = webdriver.Chrome()

#浏览器最大化
driver.maximize_window()

#打开主页
driver.get("http://10.65.205.90:7273/webapp/login")

#获取域名名密码等，并输入
driver.find_element_by_id("username").send_keys('jsadmin')
driver.find_element_by_id("password").send_keys('zkjn')
driver.find_element_by_class_name('login_btn').click()

#依次点击菜单系统配置
time.sleep(3)
driver.find_element_by_xpath("//*[text()='系统配置']").click()
time.sleep(3)
driver.find_element_by_xpath("//*[text()='对象及主数据管理']").click()
time.sleep(3)
driver.find_element_by_xpath("//*[text()='通用基础数据管理']").click()
time.sleep(3)

iframe = driver.find_element_by_xpath('//*//div[2]/iframe')
driver.switch_to_frame(iframe)
time.sleep(3)
driver.find_element_by_xpath("//*[text()='PRJ_ONE 重点项目目录']").click()

time.sleep(20)
lista = driver.find_elements_by_css_selector(".datagrid-view2 .tree-hit.tree-collapsed")
#抓取页面元素

for x in lista:
    x.click()
    time.sleep(0.3)


time.sleep(3)
code = driver.find_elements_by_css_selector('.datagrid-btable .datagrid-row [field=code] .tree-title')
name = driver.find_elements_by_css_selector('.datagrid-btable .datagrid-row [field=name] div')
a = code.__len__()
ae=[]
be=[]
for x in code:
    ae.append(x.text)
print('--------------------------------------------------------------------')
for y in name:
    be.append(y.text)
print('--------------------------------------------------------------------')
for z in range(a):
    #print(ae[z],'|',be[z])
    
    file_obj.writelines(ae[z],'|',be[z])
    file_obj.write('\n')
