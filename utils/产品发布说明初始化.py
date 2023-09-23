import datetime
import sys

import openpyxl

"""
每个版本执行一次, 初始化

传入版本参数

python /home/zhaozhiwei/workspace/python/utils/产品发布说明初始化.py PAYZJ VERSION

"""
if __name__ == '__main__':
    # 获取当前日期
    now = datetime.date.today()
    print(now)
    # 获取年 月
    year = now.year
    month = now.month
    day = now.day

    # appid = "PAYZJ"
    # version = "4_0_4_8"

    # 读取命令行参数
    appid = sys.argv[1]
    version = sys.argv[2]

    # 读取发布计划中内容, 用来填充发布说明
    if appid == "NFCS" or appid == "ISA":
        fbFile = '/mnt/d/codetag/' + appid.upper() + '/V' + version + '/发布说明/' + appid + '_V_' + version + '版本发布计划.xlsx'
    else:
        fbFile = '/mnt/d/codetag/ifmis-spring-cloud4.0/' + appid.lower() + '/V' + version + '/发布说明/' + appid + '_V_' + version + '版本发布计划.xlsx'
    wb = openpyxl.load_workbook(fbFile, False)
    sheet = wb['版本发布计划']

    print('Reading 版本发布计划 rows...')
    allRows = []
    for row in range(9, len(tuple(sheet.rows))):
        rowData = {}
        # 从第9行开始获取数据, c列为内容, d列为禅道号
        content = sheet['C' + str(row)].value
        srcId = sheet['D' + str(row)].value
        rowData['content'] = content
        rowData['srcId'] = srcId
        allRows.append(rowData)

    wb.close()

    # 调整发布说明内容
    if appid.upper() == "NFCS" or appid.upper() == "ISA":
        fbFile = '/mnt/d/codetag/' + appid.upper() + '/V' + version + '/发布说明/产品发布说明模板.xlsx'
    else:
        fbFile = '/mnt/d/codetag/ifmis-spring-cloud4.0/' + appid.lower() + '/V' + version + '/发布说明/产品发布说明模板.xlsx'
    wb = openpyxl.load_workbook(fbFile, False)
    sheet = wb['01_发版说明']
    # 修改版本信息等
    # 产品标识
    sheet['F2'].value = appid
    # 发布日期
    sheet['H2'].value = "{}月{}日".format(month, day)
    sheet['H14'].value = "{}月{}日".format(month, day)

    # 系统版本号
    sheet['C7'].value = version.replace("_", ".")
    sheet['C8'].value = version.replace("_", ".")
    if appid.upper() == "NFCS":
        # 部署文件名 ifmis-pay-service-4.0.3.6-SNAPSHOT.jar
        sheet['E7'].value = "ifmis-data-center-{}-SNAPSHOT.jar".format(version.replace("_", "."))
        sheet['E8'].value = ""
    if appid.upper() == "ISA":
        sheet['E7'].value = "ifmis-service-agent-{}-SNAPSHOT.jar".format(version.replace("_", "."))
        sheet['E8'].value = ""
    else:
        # 部署文件名 ifmis-pay-service-4.0.3.6-SNAPSHOT.jar
        sheet['E7'].value = "ifmis-{}-service-{}-SNAPSHOT.jar".format(appid.lower(), version.replace("_", "."))
        sheet['E8'].value = "ifmis-{}-webapp-{}-SNAPSHOT.jar".format(appid.lower(), version.replace("_", "."))
    # 数据库版本
    sheet['G7'].value = version.replace("_", ".")
    sheet['G8'].value = version.replace("_", ".")

    # 02_发版测试
    sheet = wb['02_发版测试']
    sheet['F2'].value = "{}月{}日".format(month, day)
    sheet['E3'].value = "{}/{}/{}-{}/{}/{}".format(year, month-1, day, year, month, day)

    # 03_版本更新内容
    sheet = wb['03_版本更新内容']
    # 遍历数据增加行填充数据
    for rowIndex in range(0, len(allRows)):
        rowData = allRows[rowIndex]
        # 行填充, (行, 列, 值)
        sheet.cell(rowIndex + 3, 1, rowIndex + 1)
        srcId = rowData['srcId']
        sheet.cell(rowIndex + 3, 2,
                   '问题' if srcId is not None and str(srcId).__contains__("#") else '需求')
        sheet.cell(rowIndex + 3, 3, rowIndex + 1)
        if appid.upper() == "NFCS":
            sheet.cell(rowIndex + 3, 4, '人大联网监督系统')
            sheet.cell(rowIndex + 3, 5, '人大联网监督系统')
        if appid.upper() == "ISA" :
            sheet.cell(rowIndex + 3, 4, '单位端数据交换服务')
            sheet.cell(rowIndex + 3, 5, '单位端数据交换服务')
        else:
            sheet.cell(rowIndex + 3, 4, '预算执行')
            if appid.upper() == "GFBI":
                sheet.cell(rowIndex + 3, 5, '预算执行报表')
            else:
                sheet.cell(rowIndex + 3, 5, '集中支付')
        sheet.cell(rowIndex + 3, 6, rowData['content'])
        sheet.cell(rowIndex + 3, 7, rowData['srcId'])

    # 保存
    wb.save(fbFile)
