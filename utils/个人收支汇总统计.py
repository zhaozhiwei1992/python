# !user/bin/python
# _*_ coding: utf-8 _*_
#
# @Title: 个人收支汇总统计.py
# @Description:
# 使用echart图表更直观的看个人收支情况
# 数据表格一定要统一, 行列固定
# https://pyecharts.org/#/zh-cn/quickstart
# @author zhaozhiwei
# @date 2022/9/8 上午10:05
# @version V1.0

import os

from pyecharts import options as opts
from pyecharts.charts import Bar
# 内置主题类型可查看 pyecharts.globals.ThemeType
from pyecharts.globals import ThemeType
from pyecharts.render import make_snapshot
# 使用 snapshot-selenium 渲染图片
from snapshot_selenium import snapshot

# 折线图需要
from pyecharts.charts import Line


def findAllData():
    result = {}
    """
    获取所有年度的配置信息， {“2016”:[], "2022":[]}存储
    """
    # 获取所有文件, 年度开头
    path = "/home/zhaozhiwei/Documents/notes/生活/收支"
    filesList = os.listdir(path)
    # 遍历文件
    for fileName in filesList:
        if "收入支出表" in fileName:
            print("fullName: ", path + "/" + fileName)
            # 按行读取文件内容, 并写入到对象
            f = open(path + "/" + fileName)
            # 一次读取所有行
            fileContentList = f.readlines()
            # print("文件内容", fileContentList)

            flag = False
            o_flag = False
            dataList = []
            for lineContent in fileContentList:
                # 每一次处理项目所在行开始, 直到0所在行
                if "项目" in lineContent:
                    flag = True
                    o_flag = False
                    continue
                if flag:
                    # lineContent使用|进行分割, 第一列为类型  01-14
                    rowArray = lineContent.split("|")
                    dataMap = {}
                    if len(rowArray) > 14:
                        for i in range(1, 15, 1):
                            if i == 1:
                                dataMap["项目"] = str(rowArray[1]).replace(" ", "")
                            elif i == 14:
                                tmpStr = str(rowArray[14]).replace(" ", "")
                                dataMap["合计"] = 0 if tmpStr == "" else round(float(tmpStr), 2)
                            else:
                                tmpStr = str(rowArray[i]).replace(" ", "")
                                dataMap[str(i - 1) + "月"] = 0 if tmpStr == "" else round(float(tmpStr), 2)
                        dataList.append(dataMap)
                # 其它的下一行也要搞进来, 所以多加一个标识进行处理
                if o_flag:
                    flag = False
                if "其它" in lineContent:
                    # flag = False
                    o_flag = True
            f.close()
            # print("数据存储: ", dataList)
            result[fileName] = dataList

    return result


def echart_01():
    """
    按月显示每个年度每月的收支情况
    """
    for key in datas:
        # 收入
        inPut = datas.get(key)[8]
        # 支出
        outPut = datas.get(key)[20]
        bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add_xaxis(["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"])
            .add_yaxis(key[0:4:] + "收入", list(inPut.values())[1::])
            .add_yaxis(key[0:4:] + "支出", list(outPut.values())[1::])
            .set_global_opts(title_opts=opts.TitleOpts(title=key[0:4:] + "收入", subtitle=key[0:4:] + "支出"))
        )
        make_snapshot(snapshot, bar.render("/tmp/rander.html"), "/tmp/年度收入支出分月显示柱状图_" + key[0:4:] + ".png")


def echart_02():
    """
    汇总显示每个项目的收入情况, 多个年度合计
    """
    inputSum = [0, 0, 0, 0, 0, 0, 0, 0]
    for key in datas:
        # 获取每一行的合计列
        curDatas = datas.get(key)
        # 前七行为收入
        for i in range(7):
            inputSum[i] = inputSum[i] + round(float(curDatas[i]["合计"]), 2)
    # print("项目合计金额", inputSum)

    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(["薪酬", "私活", "投资", "公积金转入", "他人转入", "报销", "退款", "其它"])
        .add_yaxis("分项目汇总收入", inputSum)
    )
    make_snapshot(snapshot, bar.render("/tmp/rander.html"), "/tmp/项目收入汇总柱状图.png")


def echart_03():
    """
    汇总显示每个项目的支出情况, 多个年度合计
    """
    inputSum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for key in datas:
        # 获取每一行的合计列
        curDatas = datas.get(key)
        # 9到19行为支出
        for i in range(9, 19):
            inputSum[i - 9] = inputSum[i - 9] + round(float(curDatas[i]["合计"]), 2)
    # print("项目合计金额", inputSum)

    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(["房租房贷", "租房水电", "餐饮", "酒店", "出行", "购物/生活用品", "充值缴费", "转账/红包", "休闲娱乐", "医疗/保险", "其它"])
        .add_yaxis("分项目汇总支出", inputSum)
    )
    make_snapshot(snapshot, bar.render("/tmp/rander.html"), "/tmp/项目支出汇总柱状图.png")


def echart_04(datas):
    """
    年度分月收入折线图

    参考: https://gallery.pyecharts.org/#/Line/stacked_line_chart
    """
    x_data = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
    line = (
        Line()
        .add_xaxis(xaxis_data=x_data)
        # .add_yaxis(
        #     series_name="搜索引擎",
        #     stack="总量",
        #     y_axis=[820, 932, 901, 934, 1290, 1330, 1320],
        #     label_opts=opts.LabelOpts(is_show=False),
        # )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="折线图堆叠"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        )
    )

    # 动态渲染y
    for key in datas:
        # 收入
        inPut = datas.get(key)[8]
        line.add_yaxis(
            series_name=key[0:4:],
            stack="总量",
            y_axis=list(inPut.values())[1::],
            label_opts=opts.LabelOpts(is_show=False),
        )

    make_snapshot(snapshot, line.render("/tmp/rander.html"), "/tmp/年度分月收入折线图.png")


def echart_05(datas):
    """
    年度分月支出折线图
    """
    x_data = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
    line = (
        Line()
        .add_xaxis(xaxis_data=x_data)
        # .add_yaxis(
        #     series_name="搜索引擎",
        #     stack="总量",
        #     y_axis=[820, 932, 901, 934, 1290, 1330, 1320],
        #     label_opts=opts.LabelOpts(is_show=False),
        # )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="折线图堆叠"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        )
    )

    # 动态渲染y
    for key in datas:
        # 收入
        outPut = datas.get(key)[20]
        line.add_yaxis(
            series_name=key[0:4:],
            stack="总量",
            y_axis=list(outPut.values())[1::],
            label_opts=opts.LabelOpts(is_show=False),
        )

    make_snapshot(snapshot, line.render("/tmp/rander.html"), "/tmp/年度分月支出折线图.png")


if __name__ == '__main__':
    # 1. 读取各个年度收支情况 集合存储
    datas = findAllData()
    # print(datas.get("2018收入支出表.org"))

    # 2. 分别生成不同的图表, 并写入到/tmp目录

    # 2.1各年度收入支出分月显示
    echart_01()

    # 2.2 项目收入汇总柱状图
    # 汇总统计多个年度, 各个收入项目, 合计列
    echart_02()

    # 2.2 项目支出汇总柱状图
    # 汇总统计多个年度, 各个支出项目
    echart_03()

    # 年度分月收入折线图
    echart_04(datas)

    # 年度分月支出折线图
    echart_05(datas)

    print("生成成功")
