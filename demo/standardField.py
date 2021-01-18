# 读取规范字段到数据库中，方便比对

#  读取excel数据
# /home/lx7ly/Documents/指标系统/规范/自动评估明细报告(2020).xlsx
import openpyxl, pprint
print('Opening workbook...')
wb = openpyxl.load_workbook('/home/lx7ly/Documents/指标系统/规范/自动评估明细报告(2020).xlsx', True)
# sheet = wb.index(1)
# sheet = wb.get_sheet_by_name('1、第五部分_生产库库表评估（1）')
sheet = wb['1、第五部分_生产库库表评估（1）']
countyData = {}

print('Reading rows...')
for row in range(2, len(tuple(sheet.rows))):
    #  获取C+F列数据
    table = sheet['C' + str(row)].value
    field = sheet['F' + str(row)].value
    if(table) and table!='小计':
        countyData[table] = field

# Open a new text file and write the contents of countyData to it.
# print('Writing results...')
# print(pprint.pformat(countyData))
# print('Done.')

import cx_Oracle
import os

# 设置查询编码
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.ZHS16GBK'
# 字段信息
# con = cx_Oracle.connect('pay_lhc170119/1@192.168.3.6/orcl')
# insertSql = []
#  类似java中 entryset
for item in countyData.items():
    # print('item中key %s value %s' %(item[0], item[1]))
#     根据value 组合成sql
#     print(item[0])
    arr = str(item[1]).split("),")
    for s in list(arr):
        # 替换数组中(变成表名+,
        s=s.replace("(", item[0]+",").replace(")","")
        # insertSql = "insert into standard_field (table_name, code, name, type, length, required) values (%s, %s, %s, %s, %s, %s)"
        tup = tuple(s.split(","))
        # print(tup)
        # print(insertSql)
        # insertSql = insertSql.format(tup)
        if(len(tup) == 6):
            print("insert into standard_field (table_name, code, name, type, length, required) values ('%s', '%s', '%s', '%s', '%s', '%s');"%(tup))

        # print(insertSql)
        # cur = con.cursor(prepared=True)
        # cur.execute(insertSql , input)

