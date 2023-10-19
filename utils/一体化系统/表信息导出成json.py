# -*- coding: utf-8 -*-

import cx_Oracle
import json

import os

"""
浙江 ppass数据库迁移
"""
# 设置查询编码
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.ZHS16GBK'
# 连接数据库 pay_33_sync/1@192.168.1.5/orcl
con = cx_Oracle.connect(os.environ['ORACLE_CONNECT'])

# 查询模板信息 对每个模板下的所有配置信息进行查询
#
# 根据查询结果 生成可重复执行delete insert语句
# 根据模板生成多个文件

cur = con.cursor()

if __name__ == "__main__":

    # 遍历表信息
    try:
        # 读取数据
        readFile = open('../tables.txt', 'r')  # r只读，w可写，a追加
        while True:
            line = readFile.readline()
            if len(line) == 0:
                break
            else:
                # 查询数据
                sql = ("select '{\"job\":{\"content\":[{\"reader\":{\"name\":\"oraclereader\","
                       "\"paramketer\":{\"column\":[' ||"
                       "       wm_concat('\"' || t.column_name || '\"') || "
                       "       '],\"connection\":[{\"jdbcUrl\":[\"jdbc:oracle:thin:@//10.40.36.194:1521/jszx\"],"
                       "\"table\":[\"tablename\"]}],\"password\":\"1\",\"username\":\"bdg_33\"}},"
                       "\"writer\":{\"name\":\"postgresqlwriter\",\"parameter\":{\"column\":[' "
                       "       || wm_concat('\"' || t.column_name || '\"') ||"
                       "       '],\"connection\":[{\"jdbcUrl\":\"jdbc:postgresql://10.142.96.168:3433/test_01\","
                       "\"table\":[\"bdg_33.tablename\"]}],\"password\":\"tjhq1234\",\"postSql\":[],\"preSql\":[\"alter "
                       "table bdg_33.fw_t_systemset disable trigger usertotemp493\"],\"username\":\"admin_ts\","
                       "\"writeMOde\":\"update\"}}}],\"setting\":{\"speed\":{\"channel\":\"32\"}}}}' ""from user_tab_cols t "
                       "where t.table_name = :table_name")

                cur.prepare(sql)
                cur.execute(None, {'table_name': line.upper()})
                res = cur.fetchall()

                # json格式化
                for result in res:
                    # 写入到json文件
                    f = open('/tmp/' + line + '.json', 'w')  # r只读，w可写，a追加
                    jsonStr = json.loads(str(result[0]))
                    formatJson = json.dumps(jsonStr, indent=1)
                    f.write(formatJson + '\n')
    finally:
        readFile.close()
