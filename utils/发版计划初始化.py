import calendar
import datetime

import openpyxl

import sys

import 项目.一堆配置 as cfg
import 项目.获取发版内容org as fborg

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

    sheet['C4'].value = cfg.APPID_NAME_MAP.get(appid)

    startRow = 9
    fbContentMap = fborg.find(appid, version)
    contentList = fbContentMap.get("content")
    # 开始写入
    # 第9行开始, C:内容 D:禅道编号, 空格分隔
    for rowIndex in range(0, len(contentList)):
        contentTuple = contentList[rowIndex]
        # 人员|内容
        sheet['C' + str(startRow + rowIndex)].value = contentTuple[0]
        # 禅道号
        sheet['D' + str(startRow + rowIndex)].value = contentTuple[1]

    # 可以另存多个
    wb.save('/tmp/{}_{}版本发布计划.xlsx'.format(appid, version))
