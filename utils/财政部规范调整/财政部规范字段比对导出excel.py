# !user/bin/python
# _*_ coding: utf-8 _*_
#
# @Title: 财政部规范字段比对导出excel.py
# @Description:
# 将财政部规范比对信息导入到excel
# @author zhaozhiwei
# @date 2022/8/4 上午11:15
# @version V1.0

import os

import cx_Oracle
import openpyxl

# 设置查询编码
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.ZHS16GBK'

# 数据库配置
ip = '192.168.100.80'
port = 1521
SID = 'ORCL'
dsn = cx_Oracle.makedsn(ip, port, SID)


def compareToExcel(tableV1, tableV2):
    """
    比较两个表数据, 分别生成表格变化, 列变化的excel
    """
    # 连接数据库
    connection = cx_Oracle.connect('PAY_34', '1', dsn)
    try:
        # 测试连接用——输出数据库版本
        print(connection.version)
        # 获取游标
        cursor = cx_Oracle.Cursor(connection)
        # v2版本增加的表
        sql = "SELECT distinct table_name_cn, table_name FROM " + tableV2 + " t1 WHERE t1.table_name NOT IN (SELECT t2.table_name FROM " + tableV1 + " t2) order by table_name asc"
        cursor.prepare(sql)
        cursor.execute(None)
        res = cursor.fetchall()
        v2AddTableDataList = []
        for result in res:
            tableObj = {}
            tableObj['table_name_cn'] = str(result[0])
            tableObj['table_name'] = str(result[1])
            tableCode = str(result[1])
            if tableCode.startswith("PAY_") or tableCode.startswith("GP_") or tableCode.startswith(
                    "INC_") or tableCode.startswith("TAX_") or tableCode.startswith("PAY_REPORT") or tableCode.startswith("GFA_") :
                    # or tableCode.startswith("ACCT_") or tableCode.startswith("GLF_")\
                v2AddTableDataList.append(tableObj)
        print("新增的表: ", v2AddTableDataList)

        # v2版本删除的表
        # 如果跟集成库比对这个不准, 生成后删掉完事儿
        sql = "SELECT distinct table_name_cn, table_name FROM " + tableV1 + " t1 WHERE t1.table_name NOT IN (SELECT t2.table_name FROM " + tableV2 + " t2)"
        cursor.prepare(sql)
        cursor.execute(None)
        res = cursor.fetchall()
        v2DelTableDataList = []
        for result in res:
            tableObj = {}
            tableObj['table_name_cn'] = str(result[0])
            tableObj['table_name'] = str(result[1])
            # v2DelTableDataList.append(tableObj)
        # 跳过删除表
        print("删除的表: ", v2DelTableDataList)

        # 获取所有v1表信息, 包含中文及英文名称, v1存在的才能考虑字段变化
        sql = "SELECT distinct table_name_cn, table_name FROM " + tableV1 + " where substr(table_name, 0,2) <> 'V_' order by table_name asc"
        cursor.prepare(sql)
        cursor.execute(None)
        res = cursor.fetchall()
        fieldCompareTableList = []
        for result in res:
            tableObj = {}
            tableObj['table_name_cn'] = str(result[0])
            tableObj['table_name'] = str(result[1])
            fieldCompareTableList.append(tableObj)

        # print('所有的表 ', fieldCompareTableList)

        addFieldList = []
        delFieldList = []
        modFieldList = []
        for tableObj in fieldCompareTableList:
            tableName = tableObj['table_name']
            tableCName = tableObj['table_name_cn']
            # v2->v1版本增加的列
            sql = "SELECT col_code, col_name, type, length, required FROM " + tableV2 + " t1 WHERE t1.table_name = '" + tableName + "' AND t1.col_code NOT IN ( SELECT t2.col_code FROM " + tableV1 + " t2 WHERE t2.table_name = '" + tableName + "')"
            cursor.prepare(sql)
            cursor.execute(None)
            res = cursor.fetchall()
            for result in res:
                fieldObj = {}
                fieldObj['table_name'] = tableName
                fieldObj['table_name_cn'] = tableCName
                fieldObj['operator'] = '新增列'
                fieldObj['col_code'] = str(result[0])
                fieldObj['col_name'] = str(result[1])
                fieldObj['type'] = str(result[2])
                fieldObj['length'] = str(result[3])
                fieldObj['required'] = str(result[4])

                if tableName.startswith("PAY_") or tableName.startswith("GP_") or tableName.startswith(
                        "INC_")  or tableCode.startswith("TAX_") or tableCode.startswith("PAY_REPORT") or tableCode.startswith("GFA_")  :
                    addFieldList.append(fieldObj)

            # v2->v1版本变更的列
            # 1.1 必填变更
            sql = "SELECT t2.col_code, t2.col_name, t2.type, t2.length, t2.required, t1.type as v2_type, t1.length as v2_length, t1.required as v2_required FROM " + tableV2 + " t1, " + tableV1 + " t2 WHERE t1.table_name = '" + tableName + "' and t2.table_name = '" + tableName + "' AND t1.col_code = t2.col_code and t1.required <> t2.required"
            cursor.prepare(sql)
            cursor.execute(None)
            res = cursor.fetchall()
            for result in res:
                fieldObj = {}
                fieldObj['table_name'] = tableName
                fieldObj['table_name_cn'] = tableCName
                fieldObj['operator'] = '必填变更'
                fieldObj['col_code'] = str(result[0])
                fieldObj['col_name'] = str(result[1])
                fieldObj['type'] = str(result[2])
                fieldObj['length'] = str(result[3])
                fieldObj['required'] = str(result[4])
                # v2部分
                fieldObj['v2_type'] = str(result[5])
                fieldObj['v2_length'] = str(result[6])
                fieldObj['v2_required'] = str(result[7])
                if tableName.startswith("PAY_") or tableName.startswith("GP_") or tableName.startswith(
                        "INC_")  or tableCode.startswith("TAX_") or tableCode.startswith("PAY_REPORT") or tableCode.startswith("GFA_") :
                    modFieldList.append(fieldObj)
            # 1.2 长度变更
            sql = "SELECT t2.col_code, t2.col_name, t2.type, t2.length, t2.required, t1.type as v2_type, t1.length as v2_length, t1.required as v2_required FROM " + tableV2 + " t1, " + tableV1 + " t2 WHERE t1.table_name = '" + tableName + "' and t2.table_name = '" + tableName + "' AND t1.col_code = t2.col_code and t1.length <> t2.length"
            cursor.prepare(sql)
            cursor.execute(None)
            res = cursor.fetchall()
            for result in res:
                # 金额的变化跳过, 基本是要按照一体化字段来处理 Currency
                # 日期的也跳过, 一体化为准, (不能跳过, 否则可能出现精度变化而丢失, 生成脚本时会处理)
                # if str(result[5]) in ["Currency", "Date", "DateTime"]:
                #     continue
                fieldObj = {}
                fieldObj['table_name'] = tableName
                fieldObj['table_name_cn'] = tableCName
                fieldObj['operator'] = '长度变更'
                fieldObj['col_code'] = str(result[0])
                fieldObj['col_name'] = str(result[1])
                fieldObj['type'] = str(result[2])
                fieldObj['length'] = str(result[3])
                fieldObj['required'] = str(result[4])
                # v2部分
                fieldObj['v2_type'] = str(result[5])
                fieldObj['v2_length'] = str(result[6])
                fieldObj['v2_required'] = str(result[7])
                if tableName.startswith("PAY_") or tableName.startswith("GP_") or tableName.startswith(
                        "INC_")  or tableCode.startswith("TAX_") or tableCode.startswith("PAY_REPORT") or tableCode.startswith("GFA_") :
                    modFieldList.append(fieldObj)
            # 1.3 类型变更
            sql = "SELECT t2.col_code, t2.col_name, t2.type, t2.length, t2.required, t1.type as v2_type, t1.length as v2_length, t1.required as v2_required FROM " + tableV2 + " t1, " + tableV1 + " t2 WHERE t1.table_name = '" + tableName + "' and t2.table_name = '" + tableName + "' AND t1.col_code = t2.col_code and t1.type <> t2.type"
            cursor.prepare(sql)
            cursor.execute(None)
            res = cursor.fetchall()
            for result in res:
                # 类型变化, 一体化和规范表的字段要有个转换, 比如NString啥的, 对于一体化跟varchar2等价, 跳过
                # 金额在规范类型Currency也跳过
                if (str(result[2]) == "VARCHAR2" and "String" in str(result[5])) or (str(result[5]) == "Currency"):
                    continue
                # 金额的变化跳过, 基本是要按照一体化字段来处理 Currency
                # 日期的也跳过, 一体化为准
                if str(result[5]) in ["Currency", "Date", "DateTime"]:
                    continue
                fieldObj = {}
                fieldObj['table_name'] = tableName
                fieldObj['table_name_cn'] = tableCName
                fieldObj['operator'] = '类型变更'
                fieldObj['col_code'] = str(result[0])
                fieldObj['col_name'] = str(result[1])
                fieldObj['type'] = str(result[2])
                fieldObj['length'] = str(result[3])
                fieldObj['required'] = str(result[4])
                # v2部分
                fieldObj['v2_type'] = str(result[5])
                fieldObj['v2_length'] = str(result[6])
                fieldObj['v2_required'] = str(result[7])
                if tableName.startswith("PAY_") or tableName.startswith("GP_") or tableName.startswith(
                        "INC_")  or tableCode.startswith("TAX_") or tableCode.startswith("PAY_REPORT") or tableCode.startswith("GFA_") :
                    modFieldList.append(fieldObj)
            # v2->v1版本删除的列
            # 跟集成库比对删除列无意义, excel中删掉即可
            sql = "SELECT col_code, col_name, type, length, required FROM " + tableV1 + " t1 WHERE t1.table_name = '" + tableName + "' AND t1.col_code NOT IN ( SELECT t2.col_code FROM " + tableV2 + " t2 WHERE t2.table_name = '" + tableName + "')"
            cursor.prepare(sql)
            cursor.execute(None)
            res = cursor.fetchall()
            for result in res:
                fieldObj = {}
                fieldObj['table_name'] = tableName
                fieldObj['table_name_cn'] = tableCName
                fieldObj['operator'] = '删除列'
                fieldObj['col_code'] = str(result[0])
                fieldObj['col_name'] = str(result[1])
                fieldObj['type'] = str(result[2])
                fieldObj['length'] = str(result[3])
                fieldObj['required'] = str(result[4])
                # 临时去掉删除列, 根据需要打开
                # if tableCode.startswith("PAY_") or tableCode.startswith("GP_") or tableCode.startswith(
                #         "INC_") or tableCode.startswith("TAX_") or tableCode.startswith("PAY_REPORT") or tableCode.startswith("GFA_") :
                    # or tableCode.startswith("ACCT_") or tableCode.startswith("GLF_")\
                    # 集成库比对, 不需要删除列，临时注释掉
                    # delFieldList.append(fieldObj)

        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print('Oracle 写入失败，Exception:{0}'.format(e))
        connection.rollback()
        connection.close()

    # 根据上述数据分别写入不同页签中
    # for sheetName in ['v2版本增加的表', 'v2版本删除的表', 'v2版本增加的列', 'v2版本修改的列', 'v2版本删除的列']:
    wb = openpyxl.load_workbook('/tmp/2.0规范表及字段变更明细模板.xlsx')
    sheet = wb['v2版本增加的表']
    for index, ele in enumerate(v2AddTableDataList):
        #  系统 表名 表名称 操作 字段名 字段名称 类型及长度 是否必填
        sheet['B' + str(index + 2)].value = ele['table_name']
        sheet['C' + str(index + 2)].value = ele['table_name_cn']

    sheet = wb['v2版本删除的表']
    for index, ele in enumerate(v2DelTableDataList):
        #  系统 表名 表名称 操作 字段名 字段名称 类型及长度 是否必填
        sheet['B' + str(index + 2)].value = ele['table_name']
        sheet['C' + str(index + 2)].value = ele['table_name_cn']

    sheet = wb['v2版本增加的列']
    for index, ele in enumerate(addFieldList):
        #  系统 表名 表名称 操作 字段名 字段名称 类型及长度 是否必填
        sheet['B' + str(index + 2)].value = ele['table_name']
        sheet['C' + str(index + 2)].value = ele['table_name_cn']
        sheet['D' + str(index + 2)].value = ele['operator']
        sheet['E' + str(index + 2)].value = ele['col_code']
        sheet['F' + str(index + 2)].value = ele['col_name']
        sheet['G' + str(index + 2)].value = ele['type'] + "(" + ele['length'] + ")"
        sheet['H' + str(index + 2)].value = ele['required']

    sheet = wb['v2版本修改的列']
    for index, ele in enumerate(modFieldList):
        #  系统 表名 表名称 操作 字段名 字段名称 类型及长度 是否必填
        sheet['B' + str(index + 2)].value = ele['table_name']
        sheet['C' + str(index + 2)].value = ele['table_name_cn']
        sheet['D' + str(index + 2)].value = ele['operator']
        sheet['E' + str(index + 2)].value = ele['col_code']
        sheet['F' + str(index + 2)].value = ele['col_name']
        sheet['G' + str(index + 2)].value = "V1: " + ele['type'] + "(" + ele['length'] + ")" + ", V2: " + ele[
            'v2_type'] + "(" + ele['v2_length'] + ")"
        sheet['H' + str(index + 2)].value = "V1: " + ele['required'] + ", V2: " + ele['v2_required']

    sheet = wb['v2版本删除的列']
    for index, ele in enumerate(delFieldList):
        #  系统 表名 表名称 操作 字段名 字段名称 类型及长度 是否必填
        sheet['B' + str(index + 2)].value = ele['table_name']
        sheet['C' + str(index + 2)].value = ele['table_name_cn']
        sheet['D' + str(index + 2)].value = ele['operator']
        sheet['E' + str(index + 2)].value = ele['col_code']
        sheet['F' + str(index + 2)].value = ele['col_name']
        sheet['G' + str(index + 2)].value = ele['type'] + "(" + ele['length'] + ")"
        sheet['H' + str(index + 2)].value = ele['required']

    wb.save('/tmp/2.0规范表及字段变更明细-全国.xlsx')


if __name__ == '__main__':
    # 生成字段比对报告, 根据两个版本表比对
    # 全国
    compareToExcel("STANDARD_FIELD_V1_JC20230505", "STANDARD_FIELD_V2_20230505")
    # 浙江
    # compareToExcel("STANDARD_FIELD_V1_ZJ20230918", "STANDARD_FIELD_V2_20230505")
