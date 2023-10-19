# !user/bin/python
# _*_ coding: utf-8 _*_
#
# @Title: 数据库建表语句生成oracle.py
# @Description: TODO 写点注释吧, 求求了
# @author zhaozhiwei
# @date 2023/10/16 上午9:49
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

def createTable(tablename):
    """
    tablename: 要生成脚本的表名
    规范和数据库字段类型对照
    XXString: varchar2
    Text: clob
    Binary: clob
    Currency: number(20, 2) 要带精度
    Integer: number
    Time: VARCHAR2(18)
    Datetime: VARCHAR2(18)
    Date: VARCHAR2(8)

    """
    tablename = tablename.upper()

    sqlList = [
        "create table " + tablename, "("]

    # 字段信息
    con = cx_Oracle.connect('pay_34/1@192.168.100.80/orcl')
    cur = con.cursor()
    sql = "select t.* from STANDARD_FIELD_V2_20230505 t where t.table_name = :table_name"
    cur.prepare(sql)
    cur.execute(None, {'table_name': tablename})
    res = cur.fetchall()
    index = len(res)

    # 列编码和名称对照
    colCodeNameMap = {}

    for result in res:
        index -= 1
        # 0          1        2        3    4      5        6
        # TABLE_NAME COL_CODE COL_NAME TYPE LENGTH REQUIRED MO
        # ('gd_NBOND MARKET_RESULT', 'NBOND_MARKET_RESULT_ID', '国债做市支持结果主键', 'String', '38', '是', 'M', None)
        columnCode = str(result[1])
        columnName = str(result[2])
        # 存储字段编码对照信息
        colCodeNameMap[columnCode] = columnName

        # 类型要特殊处理
        columnType = str(result[3])
        # 是/否
        required = str(result[5])
        requireStr = "not null" if required == "是" else ""
        if index == 0:
            if columnType.startswith("Integer"):
                # integer类型转number
                sqlList.append(columnCode + " number(" + str(result[4]) + ") " + requireStr)
            elif columnType.startswith("Currency"):
                sqlList.append(columnCode + " number(20, 2) " + requireStr)
            elif columnType.startswith("Decimal"):
                colLength = columnType[columnType.find("Decimal") + 7:]
                if "," in colLength:
                    columnType = "number" + colLength
                else:
                    columnType = "number(18, 8)"
                sqlList.append(columnCode + columnType + requireStr)
            elif columnType == "DateTime" or columnType == "Datetime" or columnType == "Time" or columnType == "datetime" or columnType == "time":
                sqlList.append(columnCode + " varchar2(18) " + requireStr)
            elif columnType == "date" or columnType == "Date":
                sqlList.append(columnCode + " varchar2(8) " + requireStr)
            elif columnType == "Text" or columnType == "Binary":
                sqlList.append(columnCode + " clob " + requireStr)
            else:
                sqlList.append(columnCode + " varchar2(" + str(result[4]) + ") " + requireStr)
        else:
            if columnType.startswith("Integer"):
                # integer类型转number
                sqlList.append(columnCode + " number(" + str(result[4]) + ") " + requireStr + ", ")
            elif columnType.startswith("Currency"):
                sqlList.append(columnCode + " number(20, 2) " + requireStr + ", ")
            elif columnType.startswith("Decimal"):
                colLength = columnType[columnType.find("Decimal") + 7:]
                if "," in colLength:
                    columnType = "number" + colLength
                else:
                    columnType = "number(18, 8)"
                sqlList.append(columnCode + columnType + requireStr)
            elif columnType == "DateTime" or columnType == "Datetime" or columnType == "Time" or columnType == "datetime" or columnType == "time":
                sqlList.append(columnCode + " varchar2(18) " + requireStr + ", ")
            elif columnType == "date" or columnType == "Date":
                sqlList.append(columnCode + " varchar2(8) " + requireStr + ", ")
            elif columnType == "Text" or columnType == "Binary":
                sqlList.append(columnCode + " clob " + requireStr + ", ")
            else:
                sqlList.append(columnCode + " varchar2(" + str(result[4]) + ") " + requireStr + ", ")

    sqlList.append(");")

    # 字段对照信息
    # for item in colCodeNameMap.items():
    #     sqlList.append(
    #         "COMMENT ON COLUMN " + tablename + "." + item[0] + " IS '" + item[1] + "';")

    return "\r\n".join(sqlList)

def createTables():
    # 连接数据库
    connection = cx_Oracle.connect('PAY_34', '1', dsn)
    try:
        # 测试连接用——输出数据库版本
        print(connection.version)
        # 获取游标
        cursor = cx_Oracle.Cursor(connection)
        # 获取要导出的表名
        sql = "SELECT distinct table_name FROM STANDARD_FIELD_V2_20230505 t1 WHERE t1.table_name like 'PAY_%' order by table_name asc"
        cursor.prepare(sql)
        cursor.execute(None)
        res = cursor.fetchall()
        createTableSqlList = []
        for result in res:
            tableName = str(result[0])
            createTableSqlList.append(createTable(tableName))
        print("\r\n".join(createTableSqlList))
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print('Oracle 写入失败，Exception:{0}'.format(e))
        connection.rollback()
        connection.close()


def getO1ConnConfig():
    # 数据库配置
    ip = '192.168.100.80'
    port = 1521
    SID = 'ORCL'
    dsn = cx_Oracle.makedsn(ip, port, SID)
    username = 'pay_34devbb'
    password = '1'
    return username, password, dsn


def getO2ConnConfig():
    # 数据库配置
    ip = '192.168.1.244'
    port = 1521
    SID = 'ORCL'
    dsn = cx_Oracle.makedsn(ip, port, SID)
    username = 'pay_dev'
    password = '1'
    return username, password, dsn

def transDataA2B(tableName):
    username, password, dsn = getO2ConnConfig()
    connection = cx_Oracle.connect(username, password, dsn)
    try:
        # 获取游标
        cursor = cx_Oracle.Cursor(connection)

        # 1. 获取目标库字段信息
        cursor.prepare("SELECT column_name FROM user_tab_columns WHERE table_name = '" + tableName + "' AND instr(column_name, '_NAME') < 1")
        cursor.execute(None)
        res = cursor.fetchall()
        tableQueryColList = []
        for result in res:
            tableQueryColList.append(str(result[0]))
        # 2. 修改目标库字段为可为空
        sql = "SELECT 'ALTER TABLE '||table_name||' MODIFY '||column_name||' NULL' FROM user_tab_columns WHERE table_name = '" + tableName + "' AND NULLABLE = 'N'";
        cursor.prepare(sql)
        cursor.execute(None)
        res = cursor.fetchall()
        for result in res:
            cursor.execute(str(result[0]))

        # 3. 查询原始库数据, 写入目标库
        username1, password1, dsn1 = getO1ConnConfig()
        connection1 = cx_Oracle.connect(username1, password1, dsn1)
        # 获取游标
        cursor1 = cx_Oracle.Cursor(connection1)
        sql = "select " + ",".join(tableQueryColList) + "  from " + tableName;
        cursor1.prepare(sql)
        cursor1.execute(None)
        res = cursor1.fetchall()
        tableDataList = []
        for result in res:
            colRow = result
            # 游标11匹配
            tableDataList.append(colRow)

        # 写入操作
        valueList = []
        for i in range(1, len(tableQueryColList) + 1):
            valueList.append(':' + str(i))
        valueStr = ",".join(valueList)

        cursor.prepare(
            'insert into ' + tableName + ' (' + ','.join(tableQueryColList) + ') '
                                                                         'values '
                                                                         '(' + valueStr + ')')
        # 执行入库
        cursor.executemany(None, tableDataList)
        connection.commit()
        cursor.close()
        connection.close()

    except Exception as e:
        print('Oracle 写入失败，Exception:{0}'.format(e))
        connection.rollback()
        connection.close()


if __name__ == '__main__':
    # 创建一堆表
    # createTables()

    # 数据迁移
    tableNameList = ['PAY_PLAN_VOUCHER', 'PAY_VOUCHER', 'PAY_VOUCHER_BILL']
    for tableName in tableNameList:
        transDataA2B(tableName)