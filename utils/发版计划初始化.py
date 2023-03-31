import calendar
import datetime

import openpyxl

import sys

"""
每个版本执行一次, 初始化

传入版本参数

python /home/zhaozhiwei/workspace/python/utils/发版计划初始化.py PAYZJ V_$VERSION

"""
if __name__ == '__main__':
    # 获取当前日期
    now = datetime.date.today()
    print(now)
    # 获取年 月
    year = now.year
    month = now.month

    # 获取总共多少周?
    # 当前月天数
    daysOfMonth = calendar.mdays[month]

    # 获取excel
    wb = openpyxl.load_workbook('/tmp/版本发布计划模板.xlsx', False)
    sheet = wb['版本发布计划']

    # appid = "PAY_ZJ"
    # version = "V_4_0_4_7"

    # 读取命令行参数
    appid = sys.argv[1]
    version = sys.argv[2]

    # 修改产品表示, 版本号, 预计发布日期
    sheet['C3'].value = appid

    # python写入单元格数据出现：‘MergedCell‘ object
    # attribute ‘value‘ is read - only
    # 处理: 给合并单元格的初始位置写数据就行, 仔细看是从哪一列开始合并的
    sheet['E4'].value = version
    sheet['E5'].value = "{}/{}/{}".format(year, month, daysOfMonth)

    # 填充发版计划内容
    srcFile = "/home/zhaozhiwei/workspace/项目管理/发版计划/"
    # 查询版本开始的内容, 循环填充
    if "GFBI" == appid:
        sheet['C4'].value = "预算执行报表系统"
        srcFile += "预算执行报表发版计划.org"
    elif "PAY" == appid:
        sheet['C4'].value = "支付系统"
        srcFile += "支付发版计划.org"
    elif "PAYZJ" == appid:
        sheet['C4'].value = "支付系统"
        srcFile += "浙江支付发版计划.org"
    elif "NFCS" == appid:
        sheet['C4'].value = "人大监督联网融合中心"
        srcFile += "人大监督联网融合中心发版计划.org"

    f = open(srcFile)
    # 一次读取所有行
    fileContentList = f.readlines()

    startRow = 8
    flag = 0
    for lineContent in fileContentList:
        # 如果找到这个版本，则准备开始写入数据, 找到需要1开始的
        # 发版计划org文件里增加了发版邮件等工具, 里面也包含版本号, 防止错误数据, 只找版本在标题上的
        if version.replace("V_", "* ") in lineContent:
            flag = 1
        if flag == 1 and "发布内容" in lineContent:
            flag = 2
        if flag == 2:
            # 开始写入
            # 第9行开始, C:内容 D:禅道编号, 空格分隔
            rowArray = lineContent.split(" ")
            if (len(rowArray)) == 3:
                # 没有禅道号的, 人员|内容
                sheet['C' + str(startRow)].value = rowArray[1] + "|" + rowArray[2]
            elif len(rowArray) > 3:
                # 人员|内容
                sheet['C' + str(startRow)].value = rowArray[2] + "|" + rowArray[3]
                # 禅道号
                sheet['D' + str(startRow)].value = rowArray[1]
            startRow = startRow+1

    # 可以另存多个
    wb.save('/tmp/{}_{}版本发布计划.xlsx'.format(appid, version))
