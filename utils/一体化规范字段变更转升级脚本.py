# !user/bin/python
# _*_ coding: utf-8 _*_
#
# @Title: 一体化规范字段变更转升级脚本.py
# @Description:
# 根据整理的新规范字段变更excel, 转换为升级脚本
# @author zhaozhiwei
# @date 2022/8/11 下午5:34
# @version V1.0

import cx_Oracle
import os

from operator import itemgetter  # itemgetter用来去dict中的key，省去了使用lambda函数
from itertools import groupby  # itertool还包含有其他很多函数，比如将多个list联合起来。。
import openpyxl

# 设置查询编码
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.ZHS16GBK'


def createTable(tablename, count):
    """
    tablename: 要生成脚本的表名
    count: 计数器，为了生成文件编号

    规范和数据库字段类型对照
    XXString: varchar2
    Text: clob
    Binary: clob
    Currency: number(16, 2) 要带精度
    Integer: number
    Time: VARCHAR2(18)
    Datetime: VARCHAR2(18)
    Date: VARCHAR2(8)

    """
    tablename = tablename.upper()
    viewname = "V_" + tablename.upper()

    sqlList = [
        # "declare",
        "   num number;",
        "begin",
        "select count(1) into num from user_constraints t where t.table_name = '" + tablename + "';",
        "if num > 0 then",
        "execute immediate 'alter table " + tablename + " drop constraint PK_" + viewname + " cascade drop index';",
        "end if;",
        "select count(1) into num from user_tables where TABLE_NAME = '" + tablename + "';",
        "if   num=1   then",
        "execute immediate 'drop table " + tablename + "';",
        "end if;",
        "execute immediate'",
        "create table " + tablename, "("]

    # 字段信息
    con = cx_Oracle.connect('pay_34/1@192.168.100.80/orcl')
    cur = con.cursor()
    sql = "select t.* from STANDARD_FIELD_V2_194 t where t.table_name = :table_name"
    cur.prepare(sql)
    cur.execute(None, {'table_name': tablename})
    res = cur.fetchall()
    index = len(res)

    # 存在MOF_DIV_CODE 和 FISCAL_YEAR 才进行分区
    partationFlag = False

    # 列编码和名称对照
    colCodeNameMap = {}

    for result in res:
        index -= 1
        # 0          1        2        3    4      5        6
        # TABLE_NAME COL_CODE COL_NAME TYPE LENGTH REQUIRED MO
        # ('PAY_NBOND MARKET_RESULT', 'NBOND_MARKET_RESULT_ID', '国债做市支持结果主键', 'String', '38', '是', 'M', None)
        columnCode = str(result[1])
        columnName = str(result[2])
        # 存储字段编码对照信息
        colCodeNameMap[columnCode] = columnName
        if columnCode == "MOF_DIV_CODE":
            partationFlag = True
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
                sqlList.append(columnCode + " number(16, 2) " + requireStr)
            elif columnType == "DateTime" or columnType == "Datetime" or columnType == "datetime" or columnType == "time":
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
                sqlList.append(columnCode + " number(" + str(result[4]) + ") " + requireStr + " ,")
            elif columnType.startswith("Currency"):
                sqlList.append(columnCode + " number(16, 2) " + requireStr + " ,")
            elif columnType == "DateTime" or columnType == "Datetime" or columnType == "datetime" or columnType == "time":
                sqlList.append(columnCode + " varchar2(18) " + requireStr + " ,")
            elif columnType == "date" or columnType == "Date":
                sqlList.append(columnCode + " varchar2(8) " + requireStr + " ,")
            elif columnType == "Text" or columnType == "Binary":
                sqlList.append(columnCode + " clob " + requireStr + " ,")
            else:
                sqlList.append(columnCode + " varchar2(" + str(result[4]) + ") " + requireStr + " ,")
    # print(len(sqlList))
    sqlList.append(")")
    if partationFlag:
        sqlList.append("partition by list (MOF_DIV_CODE)")
        sqlList.append("subpartition by list (FISCAL_YEAR)")
        sqlList.append("(")
        sqlList.append("partition P87  values (''87'')")
        sqlList.append("(")
        sqlList.append("subpartition P87_Y2016 values (''2016'')")
        sqlList.append(")")
        sqlList.append(")';")

    # 主键未定, 单独处理
    # sqlList.append("execute immediate'")
    # sqlList.append("alter table " + tablename)
    # sqlList.append("add constraint PK_" + viewname + " primary key (GUID)';")

    # 字段对照信息
    for item in colCodeNameMap.items():
        sqlList.append(
            "execute immediate 'COMMENT ON COLUMN " + tablename + "." + item[0] + " IS ''" + item[1] + "''';")

    sqlList.append("execute immediate'")
    sqlList.append("create or replace trigger TR_" + viewname + " before insert or update or delete ON " + tablename)
    sqlList.append("for each row")
    sqlList.append("begin")
    sqlList.append("if inserting then")
    sqlList.append(":new.MOF_DIV_CODE := nvl(:new.MOF_DIV_CODE, global_multyear_cz.v_pmdivid);")
    sqlList.append(":new.FISCAL_YEAR  := nvl(:new.FISCAL_YEAR, global_multyear_cz.v_pmYear);")
    sqlList.append("end if;")
    sqlList.append("end TR_" + viewname + ";';")

    sqlList.append("execute immediate'")
    sqlList.append("create or replace view " + viewname + " as")
    sqlList.append(
        "select * from " + tablename + "t  where FISCAL_YEAR= global_multyear_cz.Secu_f_GLOBAL_PARM(''YEAR'') and "
                                       "MOF_DIV_CODE = "
                                       "global_multyear_cz.Secu_f_GLOBAL_PARM(''DIVID'')';")
    # sqlList.append("end;")

    # 写入到文件中
    fileName = "/tmp/gd/" + str(count).zfill(3) + "_" + tablename + "_create_zzw.sql"

    print("fileName", fileName)
    print("fileContent", "\r\n".join(sqlList))
    if not os.path.exists(fileName):
        writeFile = open(fileName, 'a')
        try:
            # 写入
            writeFile.write("\r\n".join(sqlList))
        finally:
            writeFile.flush()
            writeFile.close()


def modifyTable(tableName, colList, count):
    """
    根据表，列变更信息, 生成脚本
    op: 新增字段, 删除字段, 修改字段
    PAY_DETAIL {'table_name': 'PAY_DETAIL', 'col_code': 'GBString(360)', 'col_type': 'GBString(360)', 'op': '新增字段'}
    """

    # 每个表字段操作可能分三种， 分别处理
    sqlList = [
        # "declare",
        "   num number;",
        "begin"
    ]
    colListGroupByOp = groupby(colList, itemgetter('op'))
    for key, group in colListGroupByOp:
        if key == "新增字段":
            for colMap in group:
                # group是一个迭代器，包含了所有的分组列表
                # print (key,g)
                colCode = colMap["col_code"]
                colType = str(colMap["col_type"])
                #  colType转换
                colType = transColType(colType)
                colName = colMap["col_name"]
                requiredStr = "not null" if str(colMap["required"]) == "是" else ""
                # 构建脚本
                sqlList.append(
                    "select count(1) into num  from user_tab_columns t where t.table_name = '" + tableName
                    + "' and t.COLUMN_NAME = '" + colCode + "';")
                sqlList.append("if   num=1   then")
                sqlList.append("ALTER TABLE " + tableName + " ADD " + colCode + " " + colType + " " + requiredStr + ";")
                sqlList.append(
                    "execute immediate 'COMMENT ON COLUMN " + tableName + "." + colCode + " IS ''" + colName + "''';")
                sqlList.append("end if;")

        elif key == "修改字段":
            for colMap in group:
                # group是一个迭代器，包含了所有的分组列表
                # print (key,g)
                colCode = colMap["col_code"]
                colType = colMap["col_type"]
                colType = transColType(colType)
                requiredStr = "not null" if str(colMap["required"]) == "是" else ""
                # 构建脚本
                sqlList.append(
                    "select count(1) into num  from user_tab_columns t where t.table_name = '" + tableName
                    + "' and t.COLUMN_NAME = '" + colCode + "';")
                sqlList.append("if   num=1   then")
                sqlList.append(
                    "ALTER TABLE " + tableName + " MODIFY " + colCode + " " + colType + " " + requiredStr + ";")
                sqlList.append("end if;")
        elif key == "删除字段":
            for colMap in group:
                colCode = colMap["col_code"]
                # 构建脚本
                sqlList.append(
                    "select count(1) into num  from user_tab_columns t where t.table_name = '" + tableName
                    + "' and t.COLUMN_NAME = '" + colCode + "';")
                sqlList.append("if   num=1   then")
                sqlList.append("ALTER TABLE " + tableName + " drop " + colCode + ";")
                sqlList.append("end if;")

    # 根据sqlList生成脚本
    # 重建视图脚本, 得判断下表是否有区划年度字段先
    # 字段信息
    con = cx_Oracle.connect('pay_34/1@192.168.100.80/orcl')
    cur = con.cursor()
    sql = "select t.* from STANDARD_FIELD_V2_194 t where t.table_name = :table_name and t.COL_CODE in (" \
          "'MOF_DIV_CODE', 'FISCAL_YEAR') "
    cur.prepare(sql)
    cur.execute(None, {'table_name': str(tableName).upper()})
    res = cur.fetchall()
    if len(res) == 2:
        sqlList.append("execute immediate'")
        sqlList.append("create or replace view V_" + tableName + " as")
        sqlList.append(
            "select * from " + tableName + "t  where FISCAL_YEAR= global_multyear_cz.Secu_f_GLOBAL_PARM(''YEAR'') and "
                                           "MOF_DIV_CODE = "
                                           "global_multyear_cz.Secu_f_GLOBAL_PARM(''DIVID'')';")

    # 写入到文件中
    fileName = "/tmp/gd/" + str(count).zfill(3) + "_" + tableName + "_modify_zzw.sql"

    print("fileName", fileName)
    print("fileContent", "\r\n".join(sqlList))
    if not os.path.exists(fileName):
        writeFile = open(fileName, 'a')
        try:
            # 写入
            writeFile.write("\r\n".join(sqlList))
        finally:
            writeFile.flush()
            writeFile.close()


def transColType(colType):
    """
    字段类型转换, 财政部格式转oracle存储格式
    """
    if colType.startswith("Integer"):
        # integer类型转number
        colType = colType.replace("Integer", "number")
    elif colType.startswith("Currency"):
        colType = "number(16, 2)"
    elif colType.startswith("DateTime") or colType.startswith("Datetime") or colType.startswith(
            "datetime") or colType.startswith("time"):
        colType = "varchar2(18)"
    elif colType.startswith("date") or colType.startswith("Date"):
        colType = "varchar2(8)"
    elif colType.startswith("Text") or colType.startswith("Binary"):
        colType = "blob"
    else:
        colType = "varchar2(" + colType.split("(")[1]
    return colType


if __name__ == '__main__':

    # 创建脚本目录
    sqlDir = '/tmp/gd/'
    if not os.path.exists(sqlDir):
        os.mkdir(sqlDir)

    # 1. excel准备好， 1为新增表, 2为字段变更
    # 2. 读取excel配置, 每个sheet分别处理, 新增表读取数据库配置创建表结构
    wb = openpyxl.load_workbook('/tmp/收入-2.0表改造生成脚本数据.xlsx', False)
    sheet = wb['sheet1']
    # 获取table_name信息列表
    count = 0
    print('sheet1 Reading rows...')
    for row in range(2, len(tuple(sheet.rows))):
        #  获取表列数据
        table = sheet['B' + str(row)].value
        if table:
            # 遍历生成创建表脚本001_xx表_create_zzw.sql, 写入/tmp/pay/下
            count = count + 1
            createTable(table, count)

    # 获取第二个页签
    sheet = wb['sheet2']
    # 转换成列及类型长度等信息
    print('sheet2 Reading rows...')
    colList = []
    for row in range(2, len(tuple(sheet.rows))):
        # 表名
        table = sheet['B' + str(row)].value
        # 新增/修改/删除 字段
        op = sheet['D' + str(row)].value
        # 列名
        colCode = sheet['E' + str(row)].value
        colName = sheet['F' + str(row)].value
        # 列类型
        colType = sheet['G' + str(row)].value
        # 必填
        required = sheet['H' + str(row)].value

        # 类型信息转换
        # if str(colType).startswith("NString"):
        #     pass
        colList.append({"table_name": table, "col_code": colCode, "col_name": colName, "col_type": colType, "op": op,
                        "required": required})

    # 根据表分组, 构建成修改脚本
    colListGroupByTableName = groupby(colList, itemgetter('table_name'))
    # for key,group in colListGroupByTableName:
    #     for g in group: #group是一个迭代器，包含了所有的分组列表
    #         print (key,g)

    # 生成表修改脚本
    # 转换为字段变化脚本, 并写入/tmp/pay下
    for key, group in colListGroupByTableName:
        count = count + 1
        modifyTable(key, group, count)

    print("处理完成......, 总共", count, "条")
