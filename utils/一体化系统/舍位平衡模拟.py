# !user/bin/python
# _*_ coding: utf-8 _*_
#
# @Title: 舍位平衡模拟.py
# @Description: 根据现场要求, 模拟舍位平衡
# @author zhaozhiwei
# @date 2023/10/9 上午9:28
# @version V1.0

import os
from operator import itemgetter
from itertools import groupby
import openpyxl
import math

def numberToColumn(num):
    result = ""
    while num > 0:
        remainder = (num - 1) % 26
        result = chr(ord('A') + remainder) + result
        num = int((num - 1) / 26)
    return result


if __name__ == '__main__':
    # 1. 配置每个sheet页签, 及标题行高
    # 如: L01, 从第三行, 第三列开始
    colParam = {'L01': 3, 'L02': 3, 'L03': 3, 'L04': 3, 'L06': 3, 'L07': 3, 'L08': 3, 'L09': 3, 'L12': 3, 'L13': 3, 'L16': 2, 'L17': 2, 'L18': 2, 'L19': 2, 'L23': 2, 'L24': 2}
    rowParam = {'L01': 3, 'L02': 3, 'L03': 4, 'L04': 4, 'L06': 5, 'L07': 5, 'L08': 3, 'L09': 3, 'L12': 3, 'L13': 4, 'L16': 3, 'L17': 4, 'L18': 4, 'L19': 3, 'L23': 6, 'L24': 3}
    # 2. 遍历读取所有数据
    wb = openpyxl.load_workbook('/mnt/d/vagrant/win7/财政总决算(录入表).xlsx', False)
    # sheetNames = wb.sheetnames
    sheetNames = colParam.keys()
    # 临时测试
    # sheetNames = ['L01']
    # 例: {L01:{'C':[100.1,200,300.1...],'D':[...]},'L02':{'B':[]}}
    allDatas = {}

    for sheetName in sheetNames:
        curSheet = wb[sheetName]
        allDatas[sheetName] = {}
        # 不同的表样表头高度可能不同, 需要特殊处理
        for row in range(rowParam[sheetName], len(tuple(curSheet.rows)) + 1):
            for col in range(colParam[sheetName], len(tuple(curSheet.columns)) + 1):
                # 按列记录每一行内容
                value = curSheet[numberToColumn(col) + str(row)].value
                if value == '':
                    value = 0
                rowObj = (str(row), value)
                if allDatas[sheetName].get(numberToColumn(col)) == None:
                    allDatas[sheetName][numberToColumn(col)] = []
                allDatas[sheetName][numberToColumn(col)].append(rowObj)
    # 3. 按列对数据进行合计, 并按列舍位平衡
    # 3.1 数据排序重组
    for item in allDatas.items():
        key = item[0]
        columns = item[1]
        for colItem in columns.items():
            colKey = colItem[0]
            colValues = colItem[1]
            # 按金额大小倒序排列 (直接改了原始值)
            colValues.sort(key=lambda x: abs(x[1]), reverse=True)
    # 3.2 根据新产生数据按列合计, 并把计算差值平摊到各个要素, 绝对值大的优先处理
    for item in allDatas.items():
        key = item[0]
        columns = item[1]
        for colItem in columns.items():
            colKey = colItem[0]
            colValues = colItem[1]
            # 原始值求和
            total = 0
            for colTuple in colValues:
                total += colTuple[1]
            # 四舍五入, 进行平衡
            total = math.ceil(total)

            # 四舍5入后求和
            newTotal = 0
            for colTuple in colValues:
                newTotal += math.ceil(colTuple[1])

            # 加1:True, 减1:False
            addFlag = None
            if total < newTotal:
                # 四舍5入后值变大, 每个都要减少一部分
                addFlag = False
            elif total > newTotal:
                addFlag = True

            # 差值
            subValue = abs(abs(total) - abs(newTotal))

            newColValues = []
            for colTuple in colValues:
                colTupleList = list(colTuple)
                colTupleList[1] = math.ceil(colTupleList[1])
                if subValue > 0:
                    # 正数+1
                    if addFlag:
                        if colTupleList[1] != 0:
                            colTupleList[1] = math.ceil(colTupleList[1]) + 1
                            subValue = subValue - 1
                    elif not addFlag:
                        if colTupleList[1] != 0:
                            colTupleList[1] = math.ceil(colTupleList[1]) - 1
                            subValue = subValue - 1
                newColValues.append(tuple(colTupleList))

            allDatas[key][colKey] = newColValues
            # allDatas[key][colKey].append((999998, total))
            # allDatas[key][colKey].append((999999, newTotal))

    # 3.3 将数据根据行号正向排列
    for item in allDatas.items():
        key = item[0]
        columns = item[1]
        for colItem in columns.items():
            colKey = colItem[0]
            colValues = colItem[1]
            # 按原始行号正向排序
            colValues.sort(key=lambda x: int(x[0]))
    # 4. 生成新的excel表数据 /mnt/d/vagrant/win7/财政总决算(录入表)-舍位平衡.xlsx
    for sheetName in sheetNames:
        curSheet = wb[sheetName]
        # 不同的表样表头高度可能不同, 需要特殊处理
        for row in range(rowParam[sheetName], len(tuple(curSheet.rows)) + 1):
            for col in range(colParam[sheetName], len(tuple(curSheet.columns)) + 1):
                curSheet[numberToColumn(col) + str(row)].value = allDatas[sheetName][numberToColumn(col)][row-rowParam[sheetName]][1]

    wb.save('/mnt/d/vagrant/win7/财政总决算(录入表)-舍位平衡.xlsx')
