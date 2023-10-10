# !user/bin/python
# _*_ coding: utf-8 _*_
#
# @Title: 财政部规范字段变更转升级脚本-全国.py
# @Description:
# 根据整理的新规范字段变更excel, 转换为升级脚本
# 转换源头有两种, 一种是通过excel格式解析生成sql
# 另一种读取数据库规范表配置, 转换成sql
# 将dic注册脚本移动到单独目录 find . -type f -name "*dic*" -exec mv {} dic \;
# @author zhaozhiwei
# @date 2022/8/11 下午5:34
# @version V1.0

import cx_Oracle
import os

# itemgetter用来去dict中的key，省去了使用lambda函数
from operator import itemgetter
# itertool还包含有其他很多函数，比如将多个list联合起来。。
from itertools import groupby
import openpyxl

# 设置查询编码
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.ZHS16GBK'


def createTable(tablename, tableNameCN, count):
    """
    tablename: 要生成脚本的表名
    count: 计数器，为了生成文件编号

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
        # 没有表才去创建
        "if   num=0   then",
        "execute immediate'",
        "create table " + tablename, "("]

    # 字段信息
    con = cx_Oracle.connect('pay_34/1@192.168.100.80/orcl')
    cur = con.cursor()
    sql = "select t.* from STANDARD_FIELD_V2_20230505 t where t.table_name = :table_name"
    cur.prepare(sql)
    cur.execute(None, {'table_name': tablename})
    res = cur.fetchall()
    index = len(res)

    # 存在MOF_DIV_CODE 和 FISCAL_YEAR 才进行分区
    partationFlag = False

    # 列编码和名称对照
    colCodeNameMap = {}

    # 表注册信息
    dicColumnsList = []
    dicColumnsList.append("begin")
    delSql = "delete from bus_t_dictable  where tablecode = '" + tablename + "';"
    dicColumnsList.append(delSql)
    insertSql = "insert into bus_t_Dictable (YEAR, PROVINCE, TABLECODE, NAME, REMARK, TABLETYPE, VERSION, DBTABNAME, " \
                "APPID, EXP, TABLEPART, ISSHOW, DBIMPFLAG, ISSYS, ISUSES, VIEWTABLENAME, DBVERSION, DATASYNC, " \
                "HASTRIGGER, SYNCCLASSNAME, STATUS)values ('2016', '87', '" + tablename + "', '" + tableNameCN + "', null, 1, " \
                                                                                          "4, '" + tablename + "', 'gd', null, '0', 1, null, 1, 1, 'V_" + tablename \
                + "', null, null, null, null, '1'); "
    dicColumnsList.append(insertSql)

    for result in res:
        index -= 1
        # 0          1        2        3    4      5        6
        # TABLE_NAME COL_CODE COL_NAME TYPE LENGTH REQUIRED MO
        # ('gd_NBOND MARKET_RESULT', 'NBOND_MARKET_RESULT_ID', '国债做市支持结果主键', 'String', '38', '是', 'M', None)
        columnCode = str(result[1])
        columnName = str(result[2])
        # 存储字段编码对照信息
        colCodeNameMap[columnCode] = columnName

        # 不创建分区表临时注释
        # if columnCode == "MOF_DIV_CODE":
            # partationFlag = True

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
                sqlList.append(columnCode + " number(20, 6) " + requireStr)
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
                sqlList.append(columnCode + " number(" + str(result[4]) + ") " + requireStr + ", ")
            elif columnType.startswith("Currency"):
                sqlList.append(columnCode + " number(20, 2) " + requireStr + ", ")
            elif columnType.startswith("Decimal"):
                sqlList.append(columnCode + " number(20, 6) " + requireStr + ", ")
            elif columnType == "DateTime" or columnType == "Datetime" or columnType == "datetime" or columnType == "time":
                sqlList.append(columnCode + " varchar2(18) " + requireStr + ", ")
            elif columnType == "date" or columnType == "Date":
                sqlList.append(columnCode + " varchar2(8) " + requireStr + ", ")
            elif columnType == "Text" or columnType == "Binary":
                sqlList.append(columnCode + " clob " + requireStr + ", ")
            else:
                sqlList.append(columnCode + " varchar2(" + str(result[4]) + ") " + requireStr + ", ")

        # 注册信息生成
        delAndInsert = dicColumns(tablename, columnCode, columnType, columnName)
        dicColumnsList.append(delAndInsert[0])
        dicColumnsList.append(delAndInsert[1])

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
        sqlList.append(")")

    sqlList.append("';")

    # 判断表不存在 count == 0才创建, 结束if
    sqlList.append("end if;")

    # 主键未定, 单独处理
    # sqlList.append("execute immediate'")
    # sqlList.append("alter table " + tablename)
    # sqlList.append("add constraint PK_" + viewname + " primary key (GUID)';")

    # 字段对照信息
    for item in colCodeNameMap.items():
        sqlList.append(
            "execute immediate 'COMMENT ON COLUMN " + tablename + "." + item[0] + " IS ''" + item[1] + "''';")

    if partationFlag:
        # 有区划年度才加这个触发器
        sqlList.append("execute immediate'")
        sqlList.append(
            "create or replace trigger TR_" + tablename + " before insert or update or delete ON " + tablename)
        sqlList.append("for each row")
        sqlList.append("begin")
        sqlList.append("if inserting then")
        sqlList.append(":new.MOF_DIV_CODE := nvl(:new.MOF_DIV_CODE, global_multyear_cz.v_pmdivid);")
        sqlList.append(":new.FISCAL_YEAR  := nvl(:new.FISCAL_YEAR, global_multyear_cz.v_pmYear);")
        sqlList.append("end if;")
        sqlList.append("end TR_" + tablename + ";';")

        # 有区划年度才家这个视图
        sqlList.append("execute immediate'")
        sqlList.append("create or replace view " + viewname + " as")
        sqlList.append(
            "select * from " + tablename + " t  where FISCAL_YEAR= global_multyear_cz.v_pmYear and "
                                           "MOF_DIV_CODE = "
                                           "global_multyear_cz.v_pmDivID';")
    # sqlList.append("end;")

    # 写入到文件中
    fileName = "/tmp/sql/" + str(count).zfill(3) + "_" + tablename + "_create_zzw.sql"

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

    dicFileName = "/tmp/sql/" + str(count).zfill(3) + "_dic_" + tablename + "_create_zzw.sql"

    if not os.path.exists(dicFileName):
        writeFile = open(dicFileName, 'a')
        try:
            # 写入
            writeFile.write("\r\n".join(dicColumnsList))
        finally:
            writeFile.flush()
            writeFile.close()


def dicColumns(tableName, colCode, colType, colName):
    """
    创建 fasp_t_diccolumn配置信息
    """
    tableName = str(tableName).upper()
    colCode = str(colCode).upper()

    sqls = []

    delSql = "delete from bus_t_diccolumn  where tablecode = '" + tableName + "' and columncode = '" + colCode + "';"
    sqls.append(delSql)

    insertSql = "insert into bus_t_diccolumn (YEAR, PROVINCE, COLUMNID, COLUMNCODE, TABLECODE, NAME, DATATYPE, " \
                "DATALENGTH, SCALE, VERSION, NULLABLE, DEFAULTVALUE, DEID, CSID, EXP, ISSYS, DBCOLUMNCODE, " \
                "ISUSES)values ('2016', '87', sys_guid(), '" + colCode + "', '" + tableName + "', '" + colName \
                + "', 'S', '100', " \
                  "null, 1, " \
                  "0, null, null, null, null, '0', '" + colCode + "', " \
                                                                  "'0'); "
    sqls.append(insertSql)
    return sqls


def modifyTable(tableName, colList, count):
    """
    根据表，列变更信息, 生成脚本
    op: 新增字段, 删除字段, 修改字段
    gd_DETAIL {'table_name': 'gd_DETAIL', 'col_code': 'GBString(360)', 'col_type': 'GBString(360)', 'op': '新增字段'}
    """

    dicColumnsList = ["begin"]

    # 每个表字段操作可能分三种， 分别处理
    sqlList = [
        # "declare",
        "   num number;",
        "begin"
    ]
    colListGroupByOp = groupby(colList, itemgetter('op'))
    for key, group in colListGroupByOp:
        if key == "新增列":
            for colMap in group:
                # group是一个迭代器，包含了所有的分组列表
                # print (key,g)
                colCode = colMap["col_code"]
                colType = str(colMap["col_type"])
                #  colType转换
                colType = addColTransColType(colType)
                colName = colMap["col_name"]
                # default 0: 如果表里已经有数据, 不指定默认值，无法新增非空字段
                requiredStr = " default 0 not null" if str(colMap["required"]) == "是" else ""
                # 构建脚本
                sqlList.append(
                    "select count(1) into num  from user_tab_columns t where t.table_name = '" + tableName
                    + "' and t.COLUMN_NAME = '" + colCode + "';")
                sqlList.append("if   num=0   then")
                sqlList.append(
                    "execute immediate 'ALTER TABLE " + tableName + " ADD " + colCode + " " + colType + " " + requiredStr + "';")
                sqlList.append(
                    "execute immediate 'COMMENT ON COLUMN " + tableName + "." + colCode + " IS ''" + colName + "''';")
                sqlList.append("end if;")

                # 生成字段注册sql, 先删后插
                delAndInsert = dicColumns(tableName, colCode, colType, colName)
                dicColumnsList.append(delAndInsert[0])
                dicColumnsList.append(delAndInsert[1])

        elif key == "必填变更" or key == "类型变更" or key == "长度变更":
            for colMap in group:
                # group是一个迭代器，包含了所有的分组列表
                # print (key,g)
                colCode = colMap["col_code"]
                if(colCode == "IS_DELETED"):
                    continue
                colType = colMap["col_type"]
                colType = modifyColTransColType(colType)
                # 构建脚本
                sqlList.append(
                    "select count(1) into num  from user_tab_columns t where t.table_name = '" + tableName
                    + "' and t.COLUMN_NAME = '" + colCode + "';")
                sqlList.append("if   num=1   then")
                # 截取colType 拆分适配polardb函数
                length = 0
                if 'numeric' in colType:
                    length = colType[colType.find("(") + 1:colType.find(",")]
                    colType = colType[:colType.find("(")]
                else:
                    length = colType[colType.find("(") + 1:colType.find(")")]
                    colType = colType[:colType.find("(")]
                sqlList.append(
                    # "execute immediate 'ALTER TABLE " + tableName + " MODIFY " + colCode + " " + colType + " " + requiredStr + "';")
                    " select fn_altertablecol('" + tableName + "', '" + colCode + "', '" + colType + "', " + length + ") into num; \n"
                    "if num = 0 then \n"
                    "return; \n"
                    "end if; \n"
                    )
                sqlList.append("end if;")

        elif key == "删除字段":
            for colMap in group:
                colCode = colMap["col_code"]
                colType = str(colMap["col_type"])
                #  colType转换
                colType = addColTransColType(colType)
                colName = colMap["col_name"]

                # 构建脚本
                sqlList.append(
                    "select count(1) into num  from user_tab_columns t where t.table_name = '" + tableName
                    + "' and t.COLUMN_NAME = '" + colCode + "';")
                sqlList.append("if   num=1   then")
                sqlList.append("execute immediate 'ALTER TABLE " + tableName + " drop column " + colCode + "';")
                sqlList.append("end if;")

                # 生成字段注册sql, 先删后插
                delAndInsert = dicColumns(tableName, colCode, colType, colName)
                # 只保留删除
                dicColumnsList.append(delAndInsert[0])

    # 根据sqlList生成脚本
    # 重建视图脚本, 得判断下表是否有区划年度字段先
    # 字段信息
    con = cx_Oracle.connect('pay_34/1@192.168.100.80/orcl')
    cur = con.cursor()
    sql = "select t.* from STANDARD_FIELD_V2_20230505 t where t.table_name = :table_name and t.COL_CODE in (" \
          "'MOF_DIV_CODE', 'FISCAL_YEAR') "
    cur.prepare(sql)
    cur.execute(None, {'table_name': str(tableName).upper()})
    res = cur.fetchall()
    if len(res) == 2:
        sqlList.append("select fn_alterview('V_" + tableName + "', \n"
                    "'create or replace view V_" + tableName + " as \n"
                    "select * from " + tableName + " where province = global_multyear_cz.v_pmDivID and year = global_multyear_cz.v_pmYear ') into num; \n"
                    "if num = 0 then \n"
                    "return; \n"
                    "end if; \n")

    # 写入到文件中
    fileName = "/tmp/sql/" + str(count).zfill(3) + "_" + tableName + "_modify_zzw.sql"

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

    dicFileName = "/tmp/sql/" + str(count).zfill(3) + "_dic_" + tableName + "_modify_zzw.sql"

    if not os.path.exists(dicFileName):
        writeFile = open(dicFileName, 'a')
        try:
            # 写入
            writeFile.write("\r\n".join(dicColumnsList))
        finally:
            writeFile.flush()
            writeFile.close()

def addColTransColType(colType):
    """
    新增字段类型转换, 财政部格式转oracle存储格式
    """
    if colType.startswith("Integer"):
        # integer类型转number
        colType = colType.replace("Integer", "numeric")
    elif colType.startswith("Currency"):
        colType = "numeric(20, 2)"
    elif colType.startswith("Decimal"):
        colType = "numeric(20, 6)"
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

def modifyColTransColType(colType):
    """
    修改字段类型转换, 财政部格式转oracle存储格式
    excel导出格式如: V1: VARCHAR2(7), V2: NString(11)
    """
    colType = colType[colType.find("V2:") + 4:]
    if colType.startswith("Integer"):
        # integer类型转number
        colType = colType.replace("Integer", "numeric")
    elif colType.startswith("Currency"):
        colType = "numeric(20, 2)"
    elif colType.startswith("Decimal"):
        colType = "numeric(20, 6)"
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
    sqlDir = '/tmp/sql/'
    if not os.path.exists(sqlDir):
        os.mkdir(sqlDir)

    # 1. excel准备好， sheet页: v2版本增加的表 v2版本删除的表 v2版本增加的列 v2版本修改的列 v2版本删除的列
    # 2. 读取excel配置, 每个sheet分别处理, 新增表读取数据库配置创建表结构
    wb = openpyxl.load_workbook('/tmp/2.0规范表及字段变更明细-浙江.xlsx', False)
    sheet = wb['v2版本增加的表']
    # 获取table_name信息列表
    # 生成脚本序号
    count = 0
    print('v2版本增加的表 Reading rows...')
    for row in range(2, len(tuple(sheet.rows)) + 1):
        #  获取表列数据
        table = sheet['B' + str(row)].value
        tableNameCN = sheet['C' + str(row)].value
        if table:
            # 遍历生成创建表脚本001_xx表_create_zzw.sql, 写入/tmp/sql/下
            count = count + 1
            createTable(table, tableNameCN, count)

    # 获取增加列页签
    sheet = wb['v2版本增加的列']
    # 转换成列及类型长度等信息
    print('v2版本增加的列 Reading rows...')
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

    # 获取修改列页签
    sheet = wb['v2版本修改的列']
    # 转换成列及类型长度等信息
    print('v2版本修改的列 Reading rows...')
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
    # 转换为字段变化脚本, 并写入/tmp/gd下
    for key, group in colListGroupByTableName:
        count = count + 1
        modifyTable(key, group, count)

    print("处理完成......, 总共", count, "条")
