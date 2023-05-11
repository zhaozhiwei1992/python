# !user/bin/python
# _*_ coding: utf-8 _*_
#
# @Title: 数据库表信息整理入库.py
# @Description:
# oracle数据库写入读取测试
# @author zhaozhiwei
# @date 2022/8/4 上午11:15
# @version V1.0

import cx_Oracle
import os

# 设置查询编码
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.ZHS16GBK'
# os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.AL32UTF8'

def getDevConnConfig():
    # 数据库配置
    ip = '192.168.100.80'
    port = 1521
    SID = 'ORCL'
    dsn = cx_Oracle.makedsn(ip, port, SID)
    username = 'PAY_34'
    password = '1'
    return username, password, dsn

def selectOrsaveDataToOracle():
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
            'insert into t_special_test (text1, text2) '
                                         'values '
                                         '(:1, :2)')

        # 执行入库, 汉字乱码， 坑
        cursor.executemany(None, ['谢䶮', '谢䶮'.encode('utf-8').decode('utf-8')])
        connection.commit()

        # print('谢䶮'.encode('utf-8'))
        # print('谢䶮'.encode('utf-8').decode('utf-8'))

        # 读取操作
        sql = 'select text1, text2 from t_special_test'
        cursor.execute(sql)
        # 获取字段描述信息

        # 列信息
        # 序号 字段名称 中文名称 类型及长度 强制 / 可选(M) 是否必填(是/否) 库表要素编号 备注
        # table_name, col_code, col_name, type, length, mo, required, table_name_cn

        res = cursor.fetchall()

        resultDatas = []
        # json格式化
        for result in res:
            colRow = result
            # 游标11匹配
            resultDatas.append(colRow)
        print(resultDatas)
        cursor.close()
        connection.close()

    except Exception as e:
        print('Oracle 写入失败，Exception:{0}'.format(e))
        connection.rollback()
        connection.close()


if __name__ == '__main__':
    # 将读取数据整理标准格式, 方便写入数据库或者excel中
    selectOrsaveDataToOracle()
