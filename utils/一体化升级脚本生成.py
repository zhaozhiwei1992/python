import cx_Oracle


def createDropTable(tablename, viewname):
    """
    生成createDrop形式的建表语句
    """
    tablename = tablename.upper()
    viewname = viewname.upper()
    sqlList = []
    sqlList.append("declare")
    sqlList.append("   num number;")
    sqlList.append("begin")
    sqlList.append("select count(1) into num from user_constraints t where t.table_name = '" + tablename + "';")
    sqlList.append("if num > 0 then")
    sqlList.append(
        "execute immediate 'alter table " + tablename + " drop constraint PK_" + viewname + " cascade drop index';")
    sqlList.append("end if;")
    sqlList.append("select count(1) into num from user_tables where TABLE_NAME = '" + tablename + "';")
    sqlList.append("if   num=1   then")
    sqlList.append("execute immediate 'drop table " + tablename + "';")
    sqlList.append("end if;")
    sqlList.append("execute immediate'")
    sqlList.append("create table " + tablename)
    sqlList.append("(")

    # 字段信息
    con = cx_Oracle.connect('pay_33_sync/1@192.168.7.6/orcl')
    # con = cx_Oracle.connect('bdg_330000/bdg330000@192.168.36.166/orcl')
    cur = con.cursor()
    sql = "select t.* from user_tab_columns t where t.table_name = :table_name"
    cur.prepare(sql)
    cur.execute(None, {'table_name': tablename})
    res = cur.fetchall()
    index = len(res)
    for result in res:
        index -= 1
        columnName = result[1]
        columnType = result[2]
        if index == 0:
            if columnType == 'NUMBER':
                sqlList.append(columnName + " " + columnType + " " + str(result[6]) + "," + str(result[7]) + " ")
            else:
                sqlList.append(columnName + " " + columnType + " " + str(result[5]) + " ")
        else:
            if columnType == 'NUMBER':
                sqlList.append(columnName + " " + columnType + " " + str(result[6]) + "," + str(result[7]) + " ,")
            else:
                sqlList.append(columnName + " " + columnType + " " + str(result[5]) + " ,")
    # print(len(sqlList))
    sqlList.append(")")
    sqlList.append("partition by list (PROVINCE)")
    sqlList.append("subpartition by list (YEAR)")
    sqlList.append("(")
    sqlList.append("partition P87  values (''87'')")
    sqlList.append("(")
    sqlList.append("subpartition P87_Y2016 values (''2016'')")
    sqlList.append(")")
    sqlList.append(")';")

    sqlList.append("execute immediate'")
    sqlList.append("alter table " + tablename)
    sqlList.append("add constraint PK_" + viewname + " primary key (GUID)';")

    sqlList.append("execute immediate'")
    sqlList.append("create or replace trigger TR_" + viewname + " before insert or update or delete ON " + tablename)
    sqlList.append("for each row")
    sqlList.append("begin")
    sqlList.append("if inserting then")
    sqlList.append(":new.province := nvl(:new.province, global_multyear_cz.v_pmdivid);")
    sqlList.append(":new.year     := nvl(:new.year, global_multyear_cz.v_pmYear);")
    sqlList.append("end if;")
    sqlList.append("end TR_" + viewname + ";';")

    sqlList.append("execute immediate'")
    sqlList.append("create or replace view " + viewname + " as")
    sqlList.append(
        "select * from " + tablename + " t  where year= global_multyear_cz.Secu_f_GLOBAL_PARM(''YEAR'') and province = "
                                       "global_multyear_cz.Secu_f_GLOBAL_PARM(''DIVID'')';")
    sqlList.append("end;")
    return "\r\n".join(sqlList)


if __name__ == '__main__':
    # tablecode
    tablename = 'PAY_APPLY_CORRECTION'
    # viewname
    viewname = 'V_PAY_APPLY_CORRECTION'
    print(createDropTable(tablename, viewname))
