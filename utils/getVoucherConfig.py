# -*- coding: utf-8 -*-
import cx_Oracle
import os

# 设置查询编码
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.ZHS16GBK'
# 连接数据库
con = cx_Oracle.connect('pay_lhc170119/1@192.168.3.6/orcl')
cur = con.cursor()

#根据系统标识获取单据配置信息,生成一系列相关脚本
#涉及表如下:
#p#fasp_t_pavoucher(单据), p#fasp_t_papage(关系), fasp_t_pubmenu(菜单), busfw_t_uixxxx, 规则表(一些过滤条件)
#俩种方式:

#根据某一个模板查询所有单据
#select * from fasp_t_pavoucher t where t.mouldid = '';
def getVouchConfigByMouldID(mouldid):
    #单据id获取菜单, 获取papage, 获取uiconfig
    pass

#select * from fasp_t_pavoucher t where t.mouldid in (select t2.guid from fasp_t_pabusinessmould t2 where t2.appid = '');
def getVoucherConfigByAppid(appid):
    condition='\'' + appid + '\''
    sqls = []
    sqls.extend(getConfigDetail("fasp_t_pavoucher", "appid", condition))
    return sqls

#select * from fasp_t_papage t where t.vchtypeid is null and t.mouldid in (select t2.guid from fasp_t_pabusinessmould t2 where t2.appid = '');
def getPapageByAppid(appid):
    condition = "select t2.guid from fasp_t_pabusinessmould t2 where t2.appid = '" + appid +"'"
    sqls = []
    sqls.extend(getConfigDetail("fasp_t_papage", "mouldid", condition))
    return sqls

#select * from fasp_t_pubmenu t where t.appid = ''
#select * from fasp_t_pubmenu t where t.param2 in (select t2.guid from fasp_t_pabusinessmould t2 where t2.appid = '');
def getPubmenuByAppid(appid):
    condition="'" + appid + "'"
    sqls = []
    sqls.extend(getConfigDetail("fasp_t_pubmenu", "appid", condition))
    return sqls

#获取所有的ui配置
# select * from busfw_t_uifunction t where t.key = '/pay/approvalform/edit/expand/button';
# select * from busfw_t_uiqueryform t where t.key = '/pay/approvalform/edit/expand/queryform';
# select * from busfw_t_uitable t where t.key = '/pay/approvalform/edit/expand/datatable';
# select * from busfw_t_uicolumn t where t.key = '/pay/approvalform/edit/expand/datatable';
# select * from busfw_t_uitable t where t.key = '/pay/approvalform/edit/expand/maindatatable';
# select * from busfw_t_uicolumn t where t.key = '/pay/approvalform/edit/expand/maindatatable';
def getUIPageByAppid(appid):
    condition =  "select t.uikey from fasp_t_papage t where t.vchtypeid is null and t.mouldid in (select t2.guid from fasp_t_pabusinessmould t2 where t2.appid = \'" + appid +"\')"
    sqls = []
    #busfw_t_uifunction
    sqls.extend(getConfigDetail("busfw_t_uifunction", "key", condition))
    sqls.extend(getConfigDetail("busfw_t_uiqueryform", "key", condition))
    sqls.extend(getConfigDetail("busfw_t_uitable", "key", condition))
    sqls.extend(getConfigDetail("busfw_t_uicolumn", "key", condition))
    sqls.extend(getConfigDetail("busfw_t_uieditform", "key", condition))
    sqls.extend(getConfigDetail("busfw_t_uitabpage", "key", condition))
    return sqls


# 根据传入信息获取dict类型数据
def getRecordSet(tablecode, pkcode, condition):
    # 获取表字段
    columns = getColumnByTablecode(tablecode.upper())

    # 查询字段 这里为了与后台转换dict时对应
    columnStr = ''
    for result in columns:
        columnStr += result[0]
        columnStr += ","
    columnStr = columnStr[0: len(columnStr) - 1]
    # 这里key信息可能修改成用in 支持的更好
    sql = 'select ' + columnStr + ' from ' + tablecode + ' t where t.' + pkcode + ' in (' + condition + ')'
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
def createDelSql(tablecode, code, condition):
    sqls = []
    sql = "delete from " + tablecode + " t where t." + code + " in (" + condition + ");"
    sqls.append(sql)
    return sqls

# 创建插入语句
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
        if (result.upper() == "GUID" or result.upper() == "COLUMNID") and (tablecode.lower() != "fasp_t_pabusinessmould"):
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

# 根据配置表及配置信息获取详细配置
def getConfigDetail(tablecode, code, condition):
    dicts = getRecordSet(tablecode, code, condition)
    sqls = []
    delsql = []
    delsql.extend(createDelSql(tablecode, code, condition))
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


if __name__ == "__main__":
    #粗暴: 所有的都根据模版id获取（从整体查询， insert脚本直接关系不明确， 程序只需要查询，做成插入脚本即可）
    sql = 'SELECT GLOBAL_MULTYEAR_CZ.SECU_F_GLOBAL_SETPARM(\'\',\'1500\',\'2017\',\'\') FROM DUAL'
    cur.execute(sql)
    appid = "bdg"
    sqls = []
    sqls.extend(getVoucherConfigByAppid(appid))
    # sqls.extend(getPubmenuByAppid(appid))
    sqls.extend(getPapageByAppid(appid))
    sqls.extend(getUIPageByAppid(appid))
    for sql in sqls:
        #encode ref
        print(sql.decode('GBK').encode('UTF-8'))
    con.close()

    #优雅: 每一级循环， 通过每个模板找到各自的多个单据， 每个单据找各自的配置， 代码中循环较多, 出来的脚本有关系
    #for loop 模版guid
    # getVouchConfigByMouldID()
    #end loop