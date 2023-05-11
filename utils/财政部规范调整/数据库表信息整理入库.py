# !user/bin/python
# _*_ coding: utf-8 _*_
#
# @Title: 数据库表信息整理入库.py
# @Description:
# 将指定数据库中表列信息导入到一个新表, 方便与财政部字段进行比对, 可用来转换升级脚本
# 可能涉及多个库, 如: 从集成库, 导入到开发库
# 配置信息不一定在一个业务库, 所以这个只能是分表前缀来进行处理, 如: PAY_, BA_BGT_, GFBI_等
# @author zhaozhiwei
# @date 2022/8/4 上午11:15
# @version V1.0

import cx_Oracle
import os

# 设置查询编码
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.ZHS16GBK'


def getJcConnConfig():
    """
    修改为集成库地址
    """
    # 数据库配置
    ip = '192.168.100.81'
    port = 1521
    SID = 'ORCL'
    dsn = cx_Oracle.makedsn(ip, port, SID)
    username = 'pay_34jz_2022test'
    password = 'longtu34'
    return username, password, dsn


def getDevConnConfig():
    # 数据库配置
    ip = '192.168.100.80'
    port = 1521
    SID = 'ORCL'
    dsn = cx_Oracle.makedsn(ip, port, SID)
    username = 'PAY_34'
    password = '1'
    return username, password, dsn


def getFieldDataListFromJC():
    """
    获取指定环境表配置信息
    """
    tableColList = []
    username, password, dsn = getJcConnConfig()
    connection = cx_Oracle.connect(username, password, dsn)
    try:
        # 测试连接用——输出数据库版本
        print(connection.version)
        # 获取游标
        cursor = cx_Oracle.Cursor(connection)
        # 设置财政区划
        sql = "select GLOBAL_MULTYEAR_CZ.SECU_F_GLOBAL_SETPARM('', '340000000', '2022', '') from dual"
        cursor.execute(sql)
        # 获取数据库中表定义信息
        # 这里查询字段要跟后边导入匹配上
        sql = (
            "SELECT t.TABLE_NAME, t.column_name, t4.name AS col_comments, t.data_type, t.data_length, DECODE(t.nullable, 'Y', 'N', 'M') AS mo, DECODE(t.nullable, 'Y', '否', '是') AS required, t3.name as table_name_cn "
            "FROM user_tab_cols t, user_col_comments t2, fasp_t_dictable t3, FASP_T_DICCOLUMN t4 WHERE t.table_name = t2.table_name (+) AND t.column_name = t2.column_name (+) AND t.table_name = t3.TABLECODE(+) AND t.table_name = t4.TABLECODE(+) AND t.COLUMN_NAME = t4.COLUMNCODE(+)")
        cursor.execute(sql)
        # 获取字段描述信息

        # 列信息
        # 序号 字段名称 中文名称 类型及长度 强制 / 可选(M) 是否必填(是/否) 库表要素编号 备注
        # table_name, col_code, col_name, type, length, mo, required, table_name_cn

        res = cursor.fetchall()

        # json格式化
        for result in res:
            colRow = result
            # 游标11匹配
            tableColList.append(colRow)
        cursor.close()
        connection.close()

    except Exception as e:
        print('Oracle 写入失败，Exception:{0}'.format(e))
        connection.rollback()
        connection.close()

    # print("表列信息", tableColList)
    return tableColList


def saveDataToOracle(tableName, tableColList):
    """
    入库
    根据表名，及表列配置信息, 批量存储配置
    程序主动提交
    """
    # 连接数据库
    username, password, dsn = getDevConnConfig()
    connection = cx_Oracle.connect(username, password, dsn)
    try:
        # 测试连接用——输出数据库版本
        print(connection.version)
        # 获取游标
        cursor = cx_Oracle.Cursor(connection)
        # 写入操作
        cursor.prepare(
            'insert into ' + tableName + ' (table_name, col_code, col_name, type, length, mo, required, table_name_cn) '
                                         'values '
                                         '(:1, :2, :3, :4, :5, :6, :7, :8)')
        # 执行入库
        cursor.executemany(None, tableColList)
        connection.commit()
        cursor.close()
        connection.close()

    except Exception as e:
        print('Oracle 写入失败，Exception:{0}'.format(e))
        connection.rollback()
        connection.close()


if __name__ == '__main__':
    # 将读取数据整理标准格式, 方便写入数据库或者excel中
    tableColList = getFieldDataListFromJC()
    print('配置信息, ', tableColList)
    saveDataToOracle("STANDARD_FIELD_V1_JC20230505", tableColList)
