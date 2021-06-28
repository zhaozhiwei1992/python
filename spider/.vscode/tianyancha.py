# import requests
# header = {
#     'Host': 'dis.tianyancha.com',
#     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
#     'Accept': 'application/json, text/plain, */*',
#     'Accept-Language': 'en-US,en;q=0.5',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Connection': 'keep-alive',
#     'Referer': 'https://dis.tianyancha.com/dis/old',
#     'Cookie': 'jsid=SEO-BING-ALL-SY-000001; TYCID=f11acc40b07c11ea866bc3a61c0ef8b0; undefined=f11acc40b07c11ea866bc3a61c0ef8b0; ssuid=1862960460; bannerFlag=false; activityTag=20200618; Hm_lvt_e92c8d65d92d534b0fc290df538b4758=1592386129; Hm_lpvt_e92c8d65d92d534b0fc290df538b4758=1592394449; _ga=GA1.2.524741309.1592386134; _gid=GA1.2.1203979956.1592386134; RTYCID=93221ad462664b088e0d78f1781d8ccf; csrfToken=OEXJRYt9yy8ntrHv9vt3ZUgT; rtoken=ae10ef976c7c473b85e988211639b124; _rutm=b414099469944f0b9f12b70bd6e71493; CT_TYCID=9a3c499fc5774097b86ed00327273df4; cloud_token=fdbac2de730c4e3ca3381c8a0520f44b; cloud_utm=05ae2718082a49a6b3a69632275a2b1b; _gat_gtag_UA_123487620_1=1'
# }

# 不可以直接访问json文件
# https://ask.hellobi.com/blog/jasmine3happy/6200
# r = requests.get(
#     'http://www.tianyancha.com/company/2316159174.json', headers=header)
# print(r.text)
# print(r.status_code)

#!/usr/bin/env python
# -*- coding:utf-8 -*-
from selenium import webdriver
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import csv

def driver_open():
    dcap = dict(DesiredCapabilities.CHROME)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"
    )
    driver = webdriver.Chrome()
    return driver

def get_content(driver,url):
    driver.get(url)
    #等待5秒，更据动态网页加载耗时自定义
    time.sleep(5)
    # 获取网页内容
    content = driver.page_source.encode('utf-8')
    driver.close()
    soup = BeautifulSoup(content, 'lxml')
    return soup

def get_basic_info(soup):
    basics = soup.select('.table.-striped-col > tbody > tr > td')

    for i,ch in enumerate(basics):
        print (i,ch.text)

    info = {}
    # 单位全名
    company = soup.select('div.company-name')[0].text.replace("\n","").replace(" ","")
    info["单位全名"]=company
    # 联系人
    fddbr = soup.select('div.name > a')[0].text
    info["法人"]=fddbr
    # 单位电话
    spans = soup.select('div.in-block.sup-ie-company-header-child-1 > span')
    info["单位电话"]=spans[1].text
    # 手机
    # 邮箱
    spans = soup.select('div.in-block.sup-ie-company-header-child-2 > span')
    info["邮箱"]=spans[1].text
    # 单位地址
    info["单位地址"]=basics[38]
    # 地区
    # 客户类别
    # 当前合作公司
    # 订货频率
    # 单词最大额
    # 现责任人
    # 现状态(正常/流失)
    info["现状态"] = basics[8]
    # 最近采购一次采购
    # 反款
    # 药厂药品生产类别
    # 备注
    # print (u'公司名称：'+company)
    # print u'法定代表人：'+fddbr
    # print u'注册资本：'+zczb
    # print u'公司状态：'+zt
    # print u'注册日期：'+zcrq
    # # print basics
    # print u'行业：'+hy
    # print u'工商注册号：'+qyzch
    # print u'企业类型：'+qylx
    # print u'组织机构代码：'+zzjgdm
    # print u'营业期限：'+yyqx
    # print u'登记机构：'+djjg
    # print u'核准日期：'+hzrq
    # print u'统一社会信用代码：'+tyshxydm
    # print (u'注册地址：'+zcdz)
    # print u'经营范围：'+jyfw
    return info

def get_csv_info():
    with open('/tmp/needs.csv')as g:
        reader = csv.reader(g)

        names=[]
        for row in reader:
            names.append(row[0])

if __name__=='__main__':

    url = "http://www.tianyancha.com/company/2316159174"

    # 获取多个单位信息
    driver = driver_open()
    soup = get_content(driver, url)
    print ('----获取基础信息----')
    infos = []
    basicinfo = get_basic_info(soup)
    infos.append(basicinfo)
    # print(infos)
    keys = basicinfo.keys()
    # 写入到excel
    with open('/tmp/result.csv','a',encoding='utf-8',newline='')as h:
        writer = csv.writer(h)
        # 集合顺序写入
        writer.writerow(keys)
        for info in infos:
            writer.writerow(info.values())
