# -*- coding: utf-8 -*-
import argparse
import uuid

import cx_Oracle
import os
import sys

# 设置查询编码
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.ZHS16GBK'


# 根据单据获取配置信息
# -- 单据配置
# select * from fasp_t_pavoucher t where t.guid = 'vchid' ;
#
# -- 配置中间表
# select * from fasp_t_papage t where t.vchtypeid = 'vchid';
#
# -- ui配置信息
# select * from busfw_t_uifunction t where t.key in (select t.uikey from P#fasp_t_papage t where t.vchtypeid = 'vchid');
# select * from busfw_t_uiqueryform t where t.key in (select t.uikey from P#fasp_t_papage t where t.vchtypeid = 'vchid');
# select * from busfw_t_uitabpage t where t.key in (select t.uikey from P#fasp_t_papage t where t.vchtypeid = 'vchid');
# select * from busfw_t_uieditform t where t.key in (select t.uikey from P#fasp_t_papage t where t.vchtypeid = 'vchid');
# select * from busfw_t_uitable t where t.key in (select t.uikey from P#fasp_t_papage t where t.vchtypeid = 'vchid');
# select * from busfw_t_uicolumn t where t.key in (select t.uikey from P#fasp_t_papage t where t.vchtypeid = 'vchid');
#
# -- 菜单配置
# select * from fasp_t_pubmenu t where t.param3 = 'vchid';
#
#
# select * from busfw_T_uitable t where t.key like '/bdg/common/srcto/index';
# select * from busfw_T_uicolumn t where t.key like '/bdg/common/srcto/index';

# 连接数据库

# 根据系统标识获取单据配置信息,生成一系列相关脚本
# 涉及表如下:
# p#fasp_t_pavoucher(单据), p#P#fasp_t_papage(关系), fasp_t_pubmenu(菜单), busfw_t_uixxxx, 规则表(一些过滤条件)
# 俩种方式:

# 根据某一个模板查询所有单据
# select * from p#fasp_t_pavoucher t where t.mouldid = '';
def getVouchConfigByMouldID(mouldid):
    """
    python 一体化单据配置导出.py --rprovince=87 --ryear=2016 --wprovince=330000000 --wyear=2021 --connstr=pay_33_sync/1@192.168.1.5/orcl --mouldid=3B1B7D3CA352A590A38278F1F9719DC5
    """
    if ARGS.connstr is None:
        raise Exception("数据库连接信息为空")
    if ARGS.mouldid is None:
        raise Exception("缺少模板id信息")

    global con
    con = cx_Oracle.connect(ARGS.connstr)
    global cur
    cur = con.cursor()
    # 单据id获取菜单, 获取papage, 获取uiconfig
    # 粗暴: 所有的都根据模版id获取（从整体查询， insert脚本直接关系不明确， 程序只需要查询，做成插入脚本即可）
    sqls = []

    # 根据模板id获取单据信息
    sqls.extend(getConfigDetail("p#fasp_t_pavoucher", " mouldid = '" + mouldid + "'"))
    # sqls.extend(getPubmenuByAppid(appid))
    # 获取papage信息
    sqls.extend(getConfigDetail("P#fasp_t_papage", " mouldid = '" + mouldid + "'"))

    condition = " key in (select t.uikey from P#fasp_t_papage t where t.vchtypeid is not null and t.mouldid in (select t2.guid from fasp_t_pabusinessmould t2 where t2.guid = \'" + mouldid + "\'))"
    # busfw_t_uifunction
    sqls.extend(getConfigDetail("p#busfw_t_uifunction", condition))
    sqls.extend(getConfigDetail("p#busfw_t_uiqueryform", condition))
    sqls.extend(getConfigDetail("p#busfw_t_uitable", condition))
    sqls.extend(getConfigDetail("p#busfw_t_uicolumn", condition))
    sqls.extend(getConfigDetail("p#busfw_t_uieditform", condition))
    sqls.extend(getConfigDetail("p#busfw_t_uitabpage", condition))

    # for sql in sqls:
    # encode ref
    # print(sql.decode('GBK').encode('UTF-8'))

    outputfile = '/tmp/bdgvouchersbymouldid.sql'
    f = open(outputfile, 'w')  # r只读，w可写，a追加
    for sql in sqls:
        # decode need by python2
        # f.write(sql.decode('GBK').encode('UTF-8') + '\n')
        f.write(sql + '\n')
    con.close()
    print("写出文件: ", outputfile)
    print("sucess ......")


# select * from p#fasp_t_pavoucher t where t.mouldid in (select t2.guid from fasp_t_pabusinessmould t2 where t2.appid = '');
def getVoucherConfigByAppid(appid="bdg"):
    condition = " appid = '" + appid + "'"
    # condition=" MOULDID in ('50BA2350F9AD4563NNJHKHknkj05186','50BA2350F9AD4563BJDKCJ3dnknj5186','50BA2350F9AD4563BJDKCJnknkj05186')"
    sqls = []
    sqls.extend(getConfigDetail("p#fasp_t_pavoucher", condition))
    return sqls


# select * from P#fasp_t_papage t where t.vchtypeid is null and t.mouldid in (select t2.guid from fasp_t_pabusinessmould t2 where t2.appid = '');
def getPapageByAppid(appid="bdg"):
    condition = " mouldid in (select t2.guid from fasp_t_pabusinessmould t2 where t2.appid = '" + appid + "')"
    sqls = []
    sqls.extend(getConfigDetail("P#fasp_t_papage", condition))
    return sqls


# select * from fasp_t_pubmenu t where t.appid = ''
# select * from fasp_t_pubmenu t where t.param2 in (select t2.guid from fasp_t_pabusinessmould t2 where t2.appid = '');
def getPubmenuByAppid(appid="bdg"):
    condition = " appid = '" + appid + "'"
    sqls = []
    sqls.extend(getConfigDetail("fasp_t_pubmenu", condition))
    return sqls


# 获取所有的ui配置
# select * from busfw_t_uifunction t where t.key = '/pay/approvalform/edit/expand/button';
# select * from busfw_t_uiqueryform t where t.key = '/pay/approvalform/edit/expand/queryform';
# select * from busfw_t_uitable t where t.key = '/pay/approvalform/edit/expand/datatable';
# select * from busfw_t_uicolumn t where t.key = '/pay/approvalform/edit/expand/datatable';
# select * from busfw_t_uitable t where t.key = '/pay/approvalform/edit/expand/maindatatable';
# select * from busfw_t_uicolumn t where t.key = '/pay/approvalform/edit/expand/maindatatable';
def getUIPageByAppid(appid="bdg"):
    condition = "key in (select t.uikey from P#fasp_t_papage t where t.vchtypeid is not null and t.mouldid in (select " \
                "t2.guid from fasp_t_pabusinessmould t2 where t2.appid = \'" + appid + "\')) "
    sqls = []
    # busfw_t_uifunction
    sqls.extend(getConfigDetail("p#busfw_t_uifunction", condition))
    sqls.extend(getConfigDetail("p#busfw_t_uiqueryform", condition))
    sqls.extend(getConfigDetail("p#busfw_t_uitable", condition))
    sqls.extend(getConfigDetail("p#busfw_t_uicolumn", condition))
    sqls.extend(getConfigDetail("p#busfw_t_uieditform", condition))
    sqls.extend(getConfigDetail("p#busfw_t_uitabpage", condition))
    return sqls


# 根据传入信息获取dict类型数据
def getRecordSet(tablecode, condition):
    # 获取表字段
    columns = getColumnByTablecode(tablecode.upper())

    # 查询字段 这里为了与后台转换dict时对应
    columnStr = ''
    for result in columns:
        columnStr += result[0]
        columnStr += ","
    columnStr = columnStr[0: len(columnStr) - 1]
    # 这里key信息可能修改成用in 支持的更好
    sql = 'select ' + columnStr + ' from ' + tablecode + ' t where (' + condition + ')'
    cur.execute(sql)
    dicts = tuple2dict(cur, columns)
    return dicts


# 返回的tuple结果集转成dict, 如果oracle支持直接转换成dict就不需要该逻辑
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


# 创建删除语句
def createDelSql(tablecode, condition):
    sqls = []
    sql = "delete from " + tablecode + " t where province = '" + ARGS.wprovince + "' and year = '" + ARGS.wyear + "' and (" + condition + "); "
    sqls.append(sql)
    return sqls


# 创建插入语句, cant update fasp_t_pabusinessmould's and fasp_t_pubmenu's guid
def createInsertSql(tablecode, map):
    sqls = []
    sql = "insert into " + tablecode + "("
    for result in map.keys():
        sql += result
        sql += ","
    sql = sql[0: len(sql) - 1]
    sql += ") values ("
    for result in map.keys():
        string = map[result.lower()]
        if (result.upper() == "GUID" or result.upper() == "COLUMNID") and (
                tablecode.lower() != "fasp_t_pabusinessmould" and tablecode.lower() != "fasp_t_pubmenu" and tablecode.lower() != "p#fasp_t_pavoucher"):
            sql += 'sys_guid()'
        elif string is None:
            sql += 'null'
        elif result.lower() == "dbversion" or result.lower() == "version":
            sql += 'null'
        elif result.lower() == "province":
            sql += "'" + ARGS.wprovince if ARGS.wprovince is not None else "87" + "'"
        elif result.lower() == "year":
            sql += "'" + ARGS.wyear if ARGS.wyear is not None else "2016" + "'"
        else:
            if isinstance(string, int) is True:
                string = str(string)
            sql += '\'' + string.replace('\'', '\'\'') + '\''
        sql += ","
    sql = sql[0: len(sql) - 1] + ");"

    sqls.append(sql)
    return sqls


# 根据配置表及配置信息获取详细配置
def getConfigDetail(tablecode, condition):
    dicts = getRecordSet(tablecode, condition)
    sqls = []
    delsql = []
    delsql.extend(createDelSql(tablecode, condition))
    for dict in dicts:
        sqls.extend(createInsertSql(tablecode, dict))
    delsql.extend(sqls)
    return delsql


def getColumnByTablecode(tablecode):
    sql = "select t.column_name from user_tab_columns t where t.table_name = :table_name"
    cur.prepare(sql)
    cur.execute(None, {'table_name': tablecode.upper()})
    res = cur.fetchall()
    return res


def generalSql():
    print("**************************************************")
    print("查数财政: " + ARGS.rprovince)
    print("查数年度: " + ARGS.ryear)
    print("写出财政: " + ARGS.wprovince)
    print("写出年度: " + ARGS.wyear)
    print("数据库连接: " + ARGS.connstr)
    print("输出路径: " + ARGS.outputfile)
    print("starting ......")

    if ARGS.connstr == "":
        raise Exception('数据库连接信息为空')

    global con
    con = cx_Oracle.connect(ARGS.connstr)
    global cur
    cur = con.cursor()

    # 粗暴: 所有的都根据模版id获取（从整体查询， insert脚本直接关系不明确， 程序只需要查询，做成插入脚本即可）
    sqls = []

    sqls.extend(getVoucherConfigByAppid(ARGS.appid))
    # sqls.extend(getPubmenuByAppid(appid))
    sqls.extend(getPapageByAppid(ARGS.appid))
    sqls.extend(getUIPageByAppid(ARGS.appid))

    # for sql in sqls:
    # encode ref
    # print(sql.decode('GBK').encode('UTF-8'))

    if ARGS.outputfile == "":
        ARGS.outputfile = "/tmp/" + uuid.uuid4().hex
    else:
        ARGS.outputfile = "/tmp/" + ARGS.outputfile
    f = open(ARGS.outputfile, 'w')  # r只读，w可写，a追加
    for sql in sqls:
        # decode need by python2
        # f.write(sql.decode('GBK').encode('UTF-8') + '\n')
        f.write(sql + '\n')
    con.close()
    print("写出文件: " + ARGS.outputfile)
    print("sucess ......")

    # 优雅: 每一级循环， 通过每个模板找到各自的多个单据， 每个单据找各自的配置， 代码中循环较多, 出来的脚本有关系
    # for loop 模版guid
    # getVouchConfigByMouldID()
    # end loop


def argparseFunc():
    """
    基于argparse模块实现高级的参数解析功能
    执行示例：
         python 一体化单据配置导出.py --rprovince=1500  --ryear=2017 -c fasp_4412/1@192.168.3.41/orcl
         python 一体化单据配置导出.py -h

    """
    parser = argparse.ArgumentParser(description="show example")  # 使用argparse的构造函数来创建对象
    parser.add_argument("-rp", "--rprovince", default="1500", help="查数财政, 默认1500：")
    parser.add_argument("-ry", "--ryear", default="2017", help="查数年度, 默认2017")
    parser.add_argument("-wp", "--wprovince", default="1500", help="写出财政, 默认1500：")
    parser.add_argument("-wy", "--wyear", default="2017", help="写出年度, 默认2017")
    parser.add_argument("-c", "--connstr", help="请输入数据库用户名密码, 例如:fasp_4412/1@192.168.3.41/orcl:")
    parser.add_argument("-o", "--outputfile", help="写出文件路径, 默认/tmp下")
    parser.add_argument("-a", "--appid", default="bdg", help="系统标识, 默认bdg")
    parser.add_argument("-m", "--mouldid", help="模板id")
    ARGS = parser.parse_args()
    print('ARGS:', ARGS)
    return ARGS

def writeVoucherConfigByAppid(appid):
    """
    单据信息写入新的区划
    """
    condition = " appid = '" + appid + "'"
    tablecode = "p#fasp_t_pavoucher"

    # 清理原数据
    sql = "delete from " + tablecode + " t where province = '" + ARGS.wprovince + "' and year = '" + ARGS.wyear + "' and (" + condition + ")"
    cur.execute(sql)
    # 写入新数据
    sql = "insert into " + tablecode + " select * from " + tablecode + " where province = '" + ARGS.wprovince + "' and year = '" + ARGS.wyear + "' and (" + condition + ")"
    cur.execute(sql)

def writeUIPageByAppid(appid):
    pass


def writePapageByAppid(appid):
    pass


def write2():
    print("**************************************************")
    print("查数财政: " + ARGS.rprovince)
    print("查数年度: " + ARGS.ryear)
    print("写出财政: " + ARGS.wprovince)
    print("写出年度: " + ARGS.wyear)
    print("数据库连接: " + ARGS.connstr)
    print("输出路径: " + ARGS.outputfile)
    print("starting ......")

    if ARGS.connstr == "":
        raise Exception('数据库连接信息为空')

    global con
    con = cx_Oracle.connect(ARGS.connstr)
    global cur
    cur = con.cursor()

    writeVoucherConfigByAppid(ARGS.appid)
    writePapageByAppid(ARGS.appid)
    writeUIPageByAppid(ARGS.appid)

    con.close()
    print("sucess ......")


if __name__ == "__main__":

    ARGS = argparseFunc()
    if ARGS.mouldid is not None:
        getVouchConfigByMouldID(ARGS.mouldid)
    elif str(ARGS.gensql) == "true":
        generalSql()
    else:
        write2()
