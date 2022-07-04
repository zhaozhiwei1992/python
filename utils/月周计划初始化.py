import calendar
import datetime
import math

import openpyxl

"""
每月1号执行一次, 初始化
"""
if __name__ == '__main__':
    # 1. 根据当前月份, 使用模版来生成当月周计划模版
    # 获取当前日期
    now = datetime.date.today()
    print(now)
    # 获取年 月
    year = now.year
    month = now.month
    month_first_weekDay = datetime.date(year, month, 1).weekday()

    # 获取总共多少周?
    # 当前月天数
    daysOfMonth = calendar.mdays[month]

    # math.ceil向上取整
    monthCount = math.ceil(daysOfMonth / 7)
    print("每月周数", monthCount)

    # 获取excel
    wb = openpyxl.load_workbook('/tmp/月周计划模板.xlsx', False)
    sheet = wb['周计划']

    print(sheet.rows)
    # 上周最后一天
    last_week_day = 0

    titleList = []
    # 每周标题: 第一周计划与报告—2022年2月7日至2月13日
    for i in range(monthCount):
        # 获取当月1号是周几, 后续时间就确定了 0-6表示周一到周天
        # 当月1号可能不是周一, 当月末有可能不是周日
        # print(month_first_weekDay)
        contentFormat = "第{}周计划与报告—{}年{}月{}日至{}月{}日"
        if (i == 0):
            last_week_day = 7 - month_first_weekDay
            title = contentFormat.format(i + 1, year, month, "1", month, last_week_day)
            # print("第%s周计划与报告—%s年%s月1日至%s月%s日" % (i + 1, year, month, month, last_week_day))
        else:
            title = contentFormat.format(i + 1, year, month, last_week_day + 1, month,
                                         daysOfMonth if (last_week_day + 7) > daysOfMonth else last_week_day + 7)
            # print("第%s周计划与报告—%s年%s月%s日至%s月%s日" % (i + 1, year, month, last_week_day+1, month, last_week_day+7))
            last_week_day += 7

        print(title)
        titleList.append(title)

    # 修改标题行内容
    for row in range(2, len(tuple(sheet.rows))):
        #  第2行, 13行, 没隔11行为本周标题行, 直接修改A列，因为A-N是合计列，都生效
        if "2" == str(row):
            sheet['A' + str(row)].value = titleList[0]
        if "13" == str(row):
            sheet['A' + str(row)].value = titleList[1]
        if "24" == str(row):
            sheet['A' + str(row)].value = titleList[2]
        if "35" == str(row):
            sheet['A' + str(row)].value = titleList[3]
        if "46" == str(row):
            sheet['A' + str(row)].value = titleList[4]

    # 可以另存多个
    wb.save('/tmp/月周计划_预算执行_支付_' + str(year) + "%02d" % month + '.xlsx')
    # wb.save('/tmp/月周计划_预算执行_浙江支付_' + str(year) + str(month) + '.xlsx')

    # 2. 传入到svn, 并提交 commit "x月周计划初始化"
