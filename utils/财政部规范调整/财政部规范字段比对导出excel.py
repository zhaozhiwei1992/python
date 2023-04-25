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
        sql = "SELECT distinct table_name_cn, table_name FROM " + tableV2 + " t1 WHERE t1.table_name NOT IN (SELECT t2.table_name FROM " + tableV1+ " t2)"
        cursor.prepare(sql)
        cursor.execute(None)
        res = cursor.fetchall()
        v2AddTableDataList=[]
        for result in res:
            tableObj={}
            tableObj['table_name_cn'] = str(result[0])
            tableObj['table_name'] = str(result[1])
            v2AddTableDataList.append(tableObj)
        print("新增的表: ", v2AddTableDataList)


        # v2版本删除的表
        sql = "SELECT distinct table_name_cn, table_name FROM " + tableV1 + " t1 WHERE t1.table_name NOT IN (SELECT t2.table_name FROM " + tableV2+ " t2)"
        cursor.prepare(sql)
        cursor.execute(None)
        res = cursor.fetchall()
        v2DelTableDataList = []
        for result in res:
            tableObj={}
            tableObj['table_name_cn'] = str(result[0])
            tableObj['table_name'] = str(result[1])
            v2DelTableDataList.append(tableObj)

        print("删除的表: ", v2DelTableDataList)

        # 获取所有v1表信息, 包含中文及英文名称, v1存在的才能考虑字段变化
        sql = "SELECT distinct table_name_cn, table_name FROM " + tableV1
        cursor.prepare(sql)
        cursor.execute(None)
        res = cursor.fetchall()
        fieldCompareTableList = []
        for result in res:
            tableObj={}
            tableObj['table_name_cn'] = str(result[0])
            tableObj['table_name'] = str(result[1])
            fieldCompareTableList.append(tableObj)

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
                addFieldList.append(fieldObj)

            # v2->v1版本变更的列
            # 1.1 必填变更
            sql = "SELECT t2.col_code, t2.col_name, t2.type, t2.length, t2.required FROM " + tableV2 + " t1, " + tableV1 + " t2 WHERE t1.table_name = '" + tableName + "' and t2.table_name = '" + tableName + "' AND t1.col_code = t2.col_code and t1.required <> t2.required"
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
                modFieldList.append(fieldObj)
            # 1.2 长度变更
            sql = "SELECT t2.col_code, t2.col_name, t2.type, t2.length, t2.required FROM " + tableV2 + " t1, " + tableV1 + " t2 WHERE t1.table_name = '" + tableName + "' and t2.table_name = '" + tableName + "' AND t1.col_code = t2.col_code and t1.length <> t2.length"
            cursor.prepare(sql)
            cursor.execute(None)
            res = cursor.fetchall()
            for result in res:
                fieldObj = {}
                fieldObj['table_name'] = tableName
                fieldObj['table_name_cn'] = tableCName
                fieldObj['operator'] = '长度变更'
                fieldObj['col_code'] = str(result[0])
                fieldObj['col_name'] = str(result[1])
                fieldObj['type'] = str(result[2])
                fieldObj['length'] = str(result[3])
                fieldObj['required'] = str(result[4])
                modFieldList.append(fieldObj)
            # 1.3 类型变更
            sql = "SELECT t2.col_code, t2.col_name, t2.type, t2.length, t2.required FROM " + tableV2 + " t1, " + tableV1 + " t2 WHERE t1.table_name = '" + tableName + "' and t2.table_name = '" + tableName + "' AND t1.col_code = t2.col_code and t1.type <> t2.type"
            cursor.prepare(sql)
            cursor.execute(None)
            res = cursor.fetchall()
            for result in res:
                fieldObj = {}
                fieldObj['table_name'] = tableName
                fieldObj['table_name_cn'] = tableCName
                fieldObj['operator'] = '类型变更'
                fieldObj['col_code'] = str(result[0])
                fieldObj['col_name'] = str(result[1])
                fieldObj['type'] = str(result[2])
                fieldObj['length'] = str(result[3])
                fieldObj['required'] = str(result[4])
                modFieldList.append(fieldObj)
            # v2->v1版本删除的列
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
                delFieldList.append(fieldObj)

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
        sheet['G' + str(index + 2)].value = ele['type'] + "(" + ele['length']+ ")"
        sheet['H' + str(index + 2)].value = ele['required']

    sheet = wb['v2版本修改的列']
    for index, ele in enumerate(modFieldList):
        #  系统 表名 表名称 操作 字段名 字段名称 类型及长度 是否必填
        sheet['B' + str(index + 2)].value = ele['table_name']
        sheet['C' + str(index + 2)].value = ele['table_name_cn']
        sheet['D' + str(index + 2)].value = ele['operator']
        sheet['E' + str(index + 2)].value = ele['col_code']
        sheet['F' + str(index + 2)].value = ele['col_name']
        sheet['G' + str(index + 2)].value = ele['type'] + "(" + ele['length']+ ")"
        sheet['H' + str(index + 2)].value = ele['required']

    sheet = wb['v2版本删除的列']
    for index, ele in enumerate(delFieldList):
        #  系统 表名 表名称 操作 字段名 字段名称 类型及长度 是否必填
        sheet['B' + str(index + 2)].value = ele['table_name']
        sheet['C' + str(index + 2)].value = ele['table_name_cn']
        sheet['D' + str(index + 2)].value = ele['operator']
        sheet['E' + str(index + 2)].value = ele['col_code']
        sheet['F' + str(index + 2)].value = ele['col_name']
        sheet['G' + str(index + 2)].value = ele['type'] + "(" + ele['length']+ ")"
        sheet['H' + str(index + 2)].value = ele['required']

    wb.save('/tmp/2.0规范表及字段变更明细.xlsx')

if __name__ == '__main__':

    # 生成字段比对报告, 根据两个版本表比对
    compareToExcel("STANDARD_FIELD_V1_STANDARD", "STANDARD_FIELD_V2_STANDARD")
