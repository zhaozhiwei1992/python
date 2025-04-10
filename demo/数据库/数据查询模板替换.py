# !user/bin/python
# _*_ coding: utf-8 _*_
"""
sql='SELECT \n    general_total_income, \n    general_income_growth, \n    central_income, \n    central_income_growth, \n    local_income, \n    local_income_growth, \n    domestic_vat, \n    domestic_vat_growth, \n    domestic_consumption_tax, \n    domestic_consumption_tax_growth, \n    corporate_income_tax, \n    corporate_income_tax_growth, \n    personal_income_tax, \n    personal_income_tax_growth, \n    import_vat_consumption_tax, \n    import_vat_consumption_tax_growth, \n    tariff, \n    tariff_growth, \n    export_refund, \n    export_refund_growth, \n    general_total_expenditure, \n    general_expenditure_growth, \n    central_expenditure, \n    central_expenditure_growth, \n    local_expenditure, \n    local_expenditure_growth \nFROM \n    general_public_budget \nWHERE \n    year = 2024 AND month = 8;\n\nSELECT \n    fund_total_income, \n    fund_income_growth, \n    central_fund_income, \n    central_fund_income_growth, \n    local_fund_income, \n    local_fund_income_growth, \n    land_sale_income, \n    land_sale_income_growth, \n    fund_total_expenditure, \n    fund_expenditure_growth, \n    central_fund_expenditure, \n    central_fund_expenditure_growth, \n    local_fund_expenditure, \n    local_fund_expenditure_growth, \n    land_sale_expenditure, \n    land_sale_expenditure_growth \nFROM \n    government_fund_budget \nWHERE \n    year = 2024 AND month = 8;' template='# {year}年{month}月财政收支报告\n\n## 一、全国一般公共预算收支情况\n这里做个总结\n### （一）一般公共预算收入情况\n- **全国一般公共预算收入**：{general_total_income}亿元，同比增长{general_income_growth}%。\n- **中央一般公共预算收入**：{central_income}亿元，同比增长{central_income_growth}%。\n- **地方一般公共预算本级收入**：{local_income}亿元，同比增长{local_income_growth}%。\n\n### （二）主要税收收入项目\n- **国内增值税**：{domestic_vat}亿元，同比增长{domestic_vat_growth}%。\n- **国内消费税**：{domestic_consumption_tax}亿元，同比增长{domestic_consumption_tax_growth}%。\n- **企业所得税**：{corporate_income_tax}亿元，同比增长{corporate_income_tax_growth}%。\n- **个人所得税**：{personal_income_tax}亿元，同比增长{personal_income_tax_growth}%。\n- **进口货物增值税、消费税**：{import_vat_consumption_tax}亿元，同比增长{import_vat_consumption_tax_growth}%。\n- **关税**：{tariff}亿元，同比增长{tariff_growth}%。\n- **出口退税**：{export_refund}亿元，同比增长{export_refund_growth}%。\n\n### （三）一般公共预算支出情况\n- **全国一般公共预算支出**：{general_total_expenditure}亿元，同比增长{general_expenditure_growth}%。\n- **中央一般公共预算本级支出**：{central_expenditure}亿元，同比增长{central_expenditure_growth}%。\n- **地方一般公共预算支出**：{local_expenditure}亿元，同比增长{local_expenditure_growth}%。\n\n## 二、全国政府性基金预算收支情况\n\n### （一）政府性基金预算收入情况\n- **全国政府性基金预算收入**：{fund_total_income}亿元，同比增长{fund_income_growth}%。\n- **中央政府性基金预算收入**：{central_fund_income}亿元，同比增长{central_fund_income_growth}%。\n- **地方政府性基金预算本级收入**：{local_fund_income}亿元，同比增长{local_fund_income_growth}%。\n  - **国有土地使用权出让收入**：{land_sale_income}亿元，同比增长{land_sale_income_growth}%。\n\n### （二）政府性基金预算支出情况\n- **全国政府性基金预算支出**：{fund_total_expenditure}亿元，同比增长{fund_expenditure_growth}%。\n- **中央政府性基金预算本级支出**：{central_fund_expenditure}亿元，同比增长{central_fund_expenditure_growth}%。\n- **地方政府性基金预算支出**：{local_fund_expenditure}亿元，同比增长{local_fund_expenditure_growth}%。\n  - **国有土地使用权出让收入相关支出**：{land_sale_expenditure}亿元，同比增长{land_sale_expenditure_growth}%。\n\n表说明:\n表1：general_public_budget（一般公共预算收支）\n字段名\t数据类型\t字段说明\nid\tNUMBER(10)\t主键，唯一标识每条记录。\nyear\tNUMBER(4)\t数据对应的年份。\nmonth\tNUMBER(2)\t数据对应的月份。\ngeneral_total_income\tNUMBER(15,2)\t全国一般公共预算总收入（单位：亿元）。\ngeneral_income_growth\tNUMBER(5,2)\t全国一般公共预算总收入的同比增长率（单位：%）。\ncentral_income\tNUMBER(15,2)\t中央一般公共预算收入（单位：亿元）。\ncentral_income_growth\tNUMBER(5,2)\t中央一般公共预算收入的同比增长率（单位：%）。\nlocal_income\tNUMBER(15,2)\t地方一般公共预算本级收入（单位：亿元）。\nlocal_income_growth\tNUMBER(5,2)\t地方一般公共预算本级收入的同比增长率（单位：%）。\ndomestic_vat\tNUMBER(15,2)\t国内增值税收入（单位：亿元）。\ndomestic_vat_growth\tNUMBER(5,2)\t国内增值税收入的同比增长率（单位：%）。\ndomestic_consumption_tax\tNUMBER(15,2)\t国内消费税收入（单位：亿元）。\ndomestic_consumption_tax_growth\tNUMBER(5,2)\t国内消费税收入的同比增长率（单位：%）。\ncorporate_income_tax\tNUMBER(15,2)\t企业所得税收入（单位：亿元）。\ncorporate_income_tax_growth\tNUMBER(5,2)\t企业所得税收入的同比增长率（单位：%）。\npersonal_income_tax\tNUMBER(15,2)\t个人所得税收入（单位：亿元）。\npersonal_income_tax_growth\tNUMBER(5,2)\t个人所得税收入的同比增长率（单位：%）。\nimport_vat_consumption_tax\tNUMBER(15,2)\t进口货物增值税、消费税收入（单位：亿元）。\nimport_vat_consumption_tax_growth\tNUMBER(5,2)\t进口货物增值税、消费税收入的同比增长率（单位：%）。\ntariff\tNUMBER(15,2)\t关税收入（单位：亿元）。\ntariff_growth\tNUMBER(5,2)\t关税收入的同比增长率（单位：%）。\nexport_refund\tNUMBER(15,2)\t出口退税金额（单位：亿元）。\nexport_refund_growth\tNUMBER(5,2)\t出口退税金额的同比增长率（单位：%）。\ngeneral_total_expenditure\tNUMBER(15,2)\t全国一般公共预算总支出（单位：亿元）。\ngeneral_expenditure_growth\tNUMBER(5,2)\t全国一般公共预算总支出的同比增长率（单位：%）。\ncentral_expenditure\tNUMBER(15,2)\t中央一般公共预算本级支出（单位：亿元）。\ncentral_expenditure_growth\tNUMBER(5,2)\t中央一般公共预算本级支出的同比增长率（单位：%）。\nlocal_expenditure\tNUMBER(15,2)\t地方一般公共预算支出（单位：亿元）。\nlocal_expenditure_growth\tNUMBER(5,2)\t地方一般公共预算支出的同比增长率（单位：%）。\n \n表2：government_fund_budget（政府性基金预算收支）\n字段名\t数据类型\t字段说明\nid\tNUMBER(10)\t主键，唯一标识每条记录。\nyear\tNUMBER(4)\t数据对应的年份。\nmonth\tNUMBER(2)\t数据对应的月份。\nfund_total_income\tNUMBER(15,2)\t全国政府性基金预算总收入（单位：亿元）。\nfund_income_growth\tNUMBER(5,2)\t全国政府性基金预算总收入的同比增长率（单位：%）。\ncentral_fund_income\tNUMBER(15,2)\t中央政府性基金预算收入（单位：亿元）。\ncentral_fund_income_growth\tNUMBER(5,2)\t中央政府性基金预算收入的同比增长率（单位：%）。\nlocal_fund_income\tNUMBER(15,2)\t地方政府性基金预算本级收入（单位：亿元）。\nlocal_fund_income_growth\tNUMBER(5,2)\t地方政府性基金预算本级收入的同比增长率（单位：%）。\nland_sale_income\tNUMBER(15,2)\t国有土地使用权出让收入（单位：亿元）。\nland_sale_income_growth\tNUMBER(5,2)\t国有土地使用权出让收入的同比增长率（单位：%）。\nfund_total_expenditure\tNUMBER(15,2)\t全国政府性基金预算总支出（单位：亿元）。\nfund_expenditure_growth\tNUMBER(5,2)\t全国政府性基金预算总支出的同比增长率（单位：%）。\ncentral_fund_expenditure\tNUMBER(15,2)\t中央政府性基金预算本级支出（单位：亿元）。\ncentral_fund_expenditure_growth\tNUMBER(5,2)\t中央政府性基金预算本级支出的同比增长率（单位：%）。\nlocal_fund_expenditure\tNUMBER(15,2)\t地方政府性基金预算支出（单位：亿元）。\nlocal_fund_expenditure_growth\tNUMBER(5,2)\t地方政府性基金预算支出的同比增长率（单位：%）。\nland_sale_expenditure\tNUMBER(15,2)\t国有土地使用权出让收入相关支出（单位：亿元）。\nland_sale_expenditure_growth\tNUMBER(5,2)\t国有土地使用权出让收入相关支出的同比'

"""

from sqlalchemyDatabase import get_db
import json
import cx_Oracle
import os

# 设置查询编码
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.ZHS16GBK'
# os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.AL32UTF8'

def getConnConfig():
    # 数据库配置
    ip = '192.168.22.132'
    port = 1521
    SID = 'ORCL'
    dsn = cx_Oracle.makedsn(ip, port, SID)
    username = 'PAY_34ST_TEST'
    password = 'longtu34'
    return username, password, dsn

def getConnection():
    username, password, dsn = getConnConfig()
    conn = cx_Oracle.connect(username, password, dsn)
    print(conn.version)
    return conn

if __name__ == '__main__':
    # db = get_db()
    connection = getConnection()

    obj = json.loads(open("./data/sql.json", "r").read())['result']

    # 1. 查询sql
    obj = json.loads(obj)
    all_sql = obj['sql'].replace("\n", "").split(";")

    resultDatas = []
    try:
        # 获取游标
        cursor = cx_Oracle.Cursor(connection)

        # 读取操作
        for sql in all_sql:
            if sql.strip() == "":
                continue
            # print(sql)
            cursor.execute(sql)
            # print(result)
            result = cursor.fetchall()
            # print(cursor.description)
            # print()
            # 以字典形式返回
            for row in result:
                colRow = dict(zip([str(col[0]).lower() for col in cursor.description], row))
                resultDatas.append(colRow)

        cursor.close()
        connection.close()

    except Exception as e:
        print('Oracle 写入失败，Exception:{0}'.format(e))
        connection.rollback()
        connection.close()
    print(resultDatas)
    # 2. 替换文本站位符
    templateText = str(obj['template']).split("表说明")[0]

    allObj = {}
    for dictRow in resultDatas:
        # 替换template
        # print(dictRow['year'])
        allObj.update(dictRow)

    templateText = templateText.format(**allObj)
    print(templateText)

