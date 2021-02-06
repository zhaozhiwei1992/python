# -*- coding: utf-8 -*-
import argparse

import cx_Oracle
import json
import re
# --查询模板 --437A05D24863A1E540612AA5NCKLKJHG
# select * from fasp_t_pabusinessmould t where t.appid = 'pay';
# select * from fasp_t_pabusinessmouldconfig t where t.mouldid = '437A05D24863A1E540612AA5NCKLKJHG';
# --
# select * from fasp_t_pabusinessmodelmenu t where t.mouldid = '437A05D24863A1E540612AA5NCKLKJHG'; --/pay/approvalform/edit
#
# select * from bus_t_pageconsole t where t.url = '/pay/approvalform/edit';
# select * from bus_t_pageconsolecomconfig t where t.url = '/pay/approvalform/edit'; --key
#
# -- 具体组件的配置信息
# select * from busfw_t_uifunction t where t.key = '/pay/approvalform/edit/expand/button';
# select * from busfw_t_uiqueryform t where t.key = '/pay/approvalform/edit/expand/queryform';
# select * from busfw_t_uitable t where t.key = '/pay/approvalform/edit/expand/datatable';
# select * from busfw_t_uicolumn t where t.key = '/pay/approvalform/edit/expand/datatable';
# select * from busfw_t_uitable t where t.key = '/pay/approvalform/edit/expand/maindatatable';
# select * from busfw_t_uicolumn t where t.key = '/pay/approvalform/edit/expand/maindatatable';
#
# select * from bus_t_pagecomponent t where t.id = 'approvalformService';
#
#
# --业务表
#
# --平台注册信息
# select * from fasp_t_dictable t where t.tablecode = '';
# select * from fasp_T_diccolumn t where t.tablecode = '';

import os

# 设置查询编码
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.ZHS16GBK'
# 连接数据库 pay_33_sync/1@192.168.1.5/orcl
con = cx_Oracle.connect(os.environ['ORACLE_CONNECT'])

# 查询模板信息 对每个模板下的所有配置信息进行查询
#
# 根据查询结果 生成可重复执行delete insert语句
# 根据模板生成多个文件

cur = con.cursor()


def getColumnByTablecode(tablecode):
    sql = "select t.column_name from user_tab_columns t where t.table_name = :table_name"
    cur.prepare(sql)
    cur.execute(None, {'table_name': tablecode.upper()})
    res = cur.fetchall()
    return res


# 创建删除语句
def createDelSql(tablecode, code, map):
    sqls = []
    sql = "delete from " + tablecode + " t where t." + code + " = '" + map[code] + "';"
    sqls.append(sql)
    return sqls


# 创建插入语句
def createInsertSql(tablecode, map):
    sqls = []
    sql = "insert into " + tablecode + "("
    for result in map.keys():
        if result.lower() == 'province' or result.lower() == 'year':
            continue
        sql += result
        sql += ","
    sql = sql[0: len(sql) - 1]
    sql += ") values ("
    for result in map.keys():
        if result.lower() == 'province' or result.lower() == 'year':
            continue
        string = map[result.lower()]
        if (result.upper() == "GUID" or result.upper() == "COLUMNID") and (
                tablecode.lower() != "fasp_t_pabusinessmould" and tablecode.lower() != "fasp_t_pabusinessmodelmenu"):
            sql += 'sys_guid()'
        elif string is None:
            sql += 'null'
        elif result.lower() == "dbversion":
            sql += 'null'
        else:
            if isinstance(string, (int)) is True:
                string = str(string)
            sql += '\'' + string.replace('\'', '\'\'') + '\''
        sql += ","
    sql = sql[0: len(sql) - 1] + ");"

    sqls.append(sql)
    return sqls


def createInsertAndDelSQL(tablecode, code, map):
    # delete sql
    sqls = createDelSql(tablecode, code, map)
    # insert sql
    sqls.extend(createInsertSql(tablecode, map))
    return sqls


def getPabusinessmouldconfig(mouldid):
    dicts = getRecordSet('fasp_t_pabusinessmouldconfig', 'mouldid', mouldid)
    sqls = []
    for dict in dicts:
        sqls = createInsertAndDelSQL('fasp_t_pabusinessmouldconfig', 'mouldid', dict)

    return sqls


def getPageconsoleByURL(url):
    global sqls
    dicts = getRecordSet('bus_t_pageconsole', 'url', url)
    for map in dicts:
        sqls = createInsertAndDelSQL('bus_t_pageconsole', 'url', map)
    return sqls


# 获取按钮区配置信息
def getUIFunction(config):
    return getConfigDetail('busfw_t_uifunction', config)


# 获取查询区配置信息
def getUIQueryform(config):
    return getConfigDetail('busfw_t_uiqueryform', config)


# 获取列表区配置信息
def getUIDatatable(config):
    return getConfigDetail('busfw_t_uitable', config)


# 获取页签配置信息
def getUITabPage(config):
    return getConfigDetail('busfw_t_uitabpage', config)


# 获取编辑区配置信息
def getUIeditform(config):
    return getConfigDetail('busfw_t_uieditform', config)


# 获取界面组件
def getPagecomponent(id):
    tablecode = 'bus_t_pagecomponent'
    dicts = getRecordSet(tablecode, 'id', id)
    sqls = []
    delsql = []
    for dict in dicts:
        if len(delsql) == 0:
            delsql.extend(createDelSql(tablecode, 'id', dict))
        sqls.extend(createInsertSql(tablecode, dict))
    delsql.extend(sqls)
    return delsql


# 根据配置表及配置信息获取详细配置
def getConfigDetail(tablecode, config):
    # 格式化成python可以解析的json格式 {"key":"value"}
    config = re.sub(r"(,?)(\w+?)\s*?:", r"\1'\2':", config).replace('\'', '\"')
    dicts = json.loads(config)
    key = dicts["key"]

    dicts = getRecordSet(tablecode, 'key', key)
    sqls = []
    delsql = []
    for dict in dicts:
        if len(delsql) == 0:
            delsql.extend(createDelSql(tablecode, 'key', dict))
        sqls.extend(createInsertSql(tablecode, dict))

    delsql.extend(sqls)
    return delsql


def getUIDatacolumns(config):
    return getConfigDetail('busfw_t_uicolumn', config)


def getPageconsolecomconfigByURL(url):
    dicts = getRecordSet('bus_t_pageconsolecomconfig', 'url', url)
    sqls = []
    delsql = []
    for dict in dicts:
        if len(delsql) == 0:
            delsql.extend(createDelSql('bus_t_pageconsolecomconfig', 'url', dict))
        sqls.extend(createInsertSql('bus_t_pageconsolecomconfig', dict))

    # 创建各个组件的脚本
    for dict in dicts:
        component = dict["componentid"]
        if component == 'bustoolbutton':
            sqls.extend(getUIFunction(dict["config"]))
        elif component == 'busqueryform':
            sqls.extend(getUIQueryform(dict["config"]))
        elif component == 'buseditform':
            sqls.extend(getUIeditform(dict["config"]))
        elif component == 'tabpage':
            sqls.extend(getUITabPage(dict["config"]))
        elif component == 'busuidatatable':
            sqls.extend(getUIDatatable(dict["config"]))
            sqls.extend(getUIDatacolumns(dict["config"]))
        elif 'Service' in component:
            sqls.extend(getPagecomponent(dict["id"]))
        else:
            pass
    delsql.extend(sqls)
    return delsql


# 根据传入信息获取dict类型数据
def getRecordSet(tablecode, pkcode, pk):
    # 获取表字段
    columns = getColumnByTablecode(tablecode.upper())

    # 查询字段 这里为了与后台转换dict时对应
    columnStr = ''
    for result in columns:
        columnStr += result[0]
        columnStr += ","
    columnStr = columnStr[0: len(columnStr) - 1]
    # 这里key信息可能修改成用in 支持的更好
    sql = 'select ' + columnStr + ' from ' + tablecode + ' t where t.' + pkcode + ' = \'' + pk + '\''
    cur.execute(sql)
    dicts = tuple2dict(cur, columns)
    return dicts


def getPabusinessmouldmenu(mouldid):
    dicts = getRecordSet('FASP_T_PABUSINESSMODELMENU', 'mouldid', mouldid)
    delsql = []
    sqls = []
    for dict in dicts:
        if len(delsql) == 0:
            delsql.extend(createDelSql('FASP_T_PABUSINESSMODELMENU', 'mouldid', dict))
        sqls.extend(createInsertSql('FASP_T_PABUSINESSMODELMENU', dict))
        sqls.extend(getPageconsoleByURL(dict["menuurl"]))
        sqls.extend(getPageconsolecomconfigByURL(dict["menuurl"]))

    delsql.extend(sqls)
    return delsql


# 返回的tuple结果集转成dict, 如果oracle支持直接转换成dict就不需要该逻辑
# json
def tuple2dict(cur, columns):
    resultSet = []
    for result in cur:
        dic = {}
        num = 0
        for res in columns:
            dic[res[0].lower()] = result[num]
            num += 1
        resultSet.append(dic)
    return resultSet


def whiletoFile(sqls):
    pass


# 获取模板信息
def getPabusinessmould(guid):
    dicts = getRecordSet('fasp_t_pabusinessmould', 'guid', guid)
    for dict in dicts:
        sqls = createInsertAndDelSQL('fasp_t_pabusinessmould', 'guid', dict)
        # extend将另一个列表的元素加入到原列表
        sqls.extend(getPabusinessmouldconfig(dict["guid"]))
        sqls.extend(getPabusinessmouldmenu(dict["guid"]))
        # for sql in sqls:
        #     print(sql)
        f = open('/tmp/mouldconfig_005_cd_zzw.sql', 'w')  # r只读，w可写，a追加
        for sql in sqls:
            f.write(sql + '\n')

            # 写入到文件
            # whiletoFile(sqls)


# 获取模板信息
def getPabusinessmouldByAppid(appid):
    dicts = getRecordSet('fasp_t_pabusinessmould', 'appid', appid)
    for dict in dicts:
        sqls = createInsertAndDelSQL('fasp_t_pabusinessmould', 'guid', dict)
        # extend将另一个列表的元素加入到原列表
        sqls.extend(getPabusinessmouldconfig(dict["guid"]))
        sqls.extend(getPabusinessmouldmenu(dict["guid"]))
        # for sql in sqls:
        #     print(sql)
        f = open('/tmp/mouldconfig_005_cd_zzw.sql', 'a')  # r只读，w可写，a追加
        for sql in sqls:
            f.write(sql + '\n')

            # 写入到文件
            # whiletoFile(sqls)


# 表注册信息
def getdictableAndColumns(tablecode):
    dictableSqls = []
    # dictable
    dicts = getRecordSet('fasp_t_dictable', 'tablecode', tablecode)
    for dict in dicts:
        dictableSqls = createInsertAndDelSQL('fasp_t_dictable', 'tablecode', dict)

    # diccolumn
    dicts = getRecordSet('fasp_t_diccolumn', 'tablecode', tablecode)
    sqls = []
    delsql = []
    for dict in dicts:
        if len(delsql) == 0:
            delsql.extend(createDelSql('fasp_t_diccolumn', 'tablecode', dict))
        sqls.extend(createInsertSql('fasp_t_diccolumn', dict))
    delsql.extend(sqls)

    dictableSqls.extend(delsql)
    return dictableSqls


def getPageconsolecomconfigByJSON(jsonstr):
    dicts = json.loads(jsonstr)
    sqls = []
    delsql = []
    for dict in dicts:
        if len(delsql) == 0:
            delsql.extend(createDelSql('bus_t_pageconsolecomconfig', 'url', dict))
        sqls.extend(createInsertSql('bus_t_pageconsolecomconfig', dict))

    # 创建各个组件的脚本
    for dict in dicts:
        component = dict["componentid"]
        if component == 'bustoolbutton':
            sqls.extend(getUIFunction(dict["config"]))
        elif component == 'busqueryform':
            sqls.extend(getUIQueryform(dict["config"]))
        elif component == 'buseditform':
            sqls.extend(getUIeditform(dict["config"]))
        elif component == 'tabpage':
            sqls.extend(getUITabPage(dict["config"]))
        elif component == 'busuidatatable':
            sqls.extend(getUIDatatable(dict["config"]))
            sqls.extend(getUIDatacolumns(dict["config"]))
        elif 'Service' in component:
            sqls.extend(getPagecomponent(dict["id"]))
        else:
            pass
    delsql.extend(sqls)
    return delsql


# 根据系统标识获取注册表
def getdictableAndColumnsByAppid(appid):
    dicts = getRecordSet('fasp_t_dictable', 'appid', appid)
    for dict in dicts:
        if dict["tablecode"] == 'BDG_T_COUNTRIES':
            continue;
        sqls = getdictableAndColumns(dict["tablecode"])
        # for sql in sqls:
        #     print(sql)
        f = open('/tmp/tabledic_zzw.sql', 'a')  # r只读，w可写，a追加
        for sql in sqls:
            f.write(sql + '\n')

            # 写入到文件
            # whiletoFile(sqls)


def argparseFunc():
    """
    基于argparse模块实现高级的参数解析功能
    执行示例：
         python getVoucherConfig.py --rprovince=1500  --ryear=2017 -c fasp_4412/1@192.168.3.41/orcl
         python getVoucherConfig.py -h

    """
    parser = argparse.ArgumentParser(description="show example")  # 使用argparse的构造函数来创建对象
    parser.add_argument("-c", "--connstr", help="请输入数据库用户名密码, 例如:fasp_4412/1@192.168.3.41/orcl:")
    parser.add_argument("-o", "--outputfile", help="写出文件路径, 默认/tmp下")
    parser.add_argument("-a", "--appid", default="bdg", help="系统标识, 默认bdg")
    parser.add_argument("-m", "--mouldid", help="模板id")
    ARGS = parser.parse_args()
    print('ARGS:', ARGS)
    return ARGS


if __name__ == "__main__":
    cur.execute("SELECT GLOBAL_MULTYEAR_CZ.SECU_F_GLOBAL_SETPARM('','87','2016','') FROM DUAL")
    # 获取界面配置信息
    ARGS = argparseFunc()
    if ARGS.mouldid is not None:
        getPabusinessmould(ARGS.mouldid)
    elif ARGS.appid is not None:
        getPabusinessmouldByAppid(ARGS.appid)

    # 获取表注册信息
    # getdictableAndColumnsByAppid("bdg")
    # sqls = getdictableAndColumns('BDG_T_BDGRECEIVEDATA')
    # for sql in sqls:
    #     print(sql)

    # f = open('/home/lx7ly/Documents/PAY_T_PAYSUBdic_zzw.sql', 'w')  # r只读，w可写，a追加
    # for sql in sqls:
    #     f.write(sql + '\n')

    # con.close()

    # annotation  todo pageconsolecomconfig jiexi
    # sqls = []
    # sqls.extend(getUIFunction('{"key":"/bdg/generaladd/summaryQuery",name:"按钮区",className:"busleftbtn"}'))
    # sqls.extend(getUIeditform('{"key":"/bdg/generaladd/summaryQuery",name:"编辑区",title:"编辑区"}'))
    # sqls.extend(getUIDatatable('{"tablecode":"FASP_T_GLCTRL","key":"/bdg/generaladd/summaryQuery",name:"追减指标",edit:true,edittableselect:true,checkbox:true,title:"追减指标", addrow:"false"}'))
    # sqls.extend(getUIDatacolumns('{"tablecode":"FASP_T_GLCTRL","key":"/bdg/generaladd/summaryQuery",name:"追减指标",edit:true,edittableselect:true,checkbox:true,title:"追减指标", addrow:"false"}'))
    # for sql in sqls:
    #     print(sql)
