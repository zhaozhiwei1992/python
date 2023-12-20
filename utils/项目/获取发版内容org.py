# !user/bin/python
# _*_ coding: utf-8 _*_
#
# @Title: 获取发版内容org.py
# @Description: 获取org发版计划内容
# @author zhaozhiwei
# @date 2023/12/20 上午10:59
# @version V1.0

import 项目.一堆配置 as cfg


def find(appid, version):
    """
    返回指定系统，固定版本发版内容
    依赖情况 [(依赖xx,版本),(依赖x2, 版本)]
    版本内容 [1.x, 2.xx, 3....]
    appid: PAYZJ (大写)
    version: V_4_1_0_0
    """
    # 填充发版计划内容
    srcFile = cfg.VER_PLAN_ORG_SRC_DIR
    # 查询版本开始的内容, 循环填充
    if "PAYZJ" == appid:
        srcFile += "浙江支付发版计划2.0.org"
    else:
        srcFile += (cfg.APPID_NAME_MAP.get(appid) + "发版计划.org")

    f = open(srcFile)
    # 一次读取所有行
    fileContentList = f.readlines()

    # 发版内容集合
    contentList = []
    # 依赖信息
    deptList = []
    startRow = 8
    flag = 0
    for lineContent in fileContentList:
        # 如果找到这个版本，则准备开始写入数据, 找到需要1开始的
        # 发版计划org文件里增加了发版邮件等工具, 里面也包含版本号, 防止错误数据, 只找版本在标题上的
        if version.replace("V_", "* ") in lineContent:
            flag = 1
        elif flag == 1 and "依赖说明" in lineContent:
            flag = 2
        elif flag == 2:
            # 写入依赖信息
            rowArray = lineContent.replace("*** ", "").split(":")
            if flag == 2 and "发布内容" in lineContent:
                flag = 3
            else:
                deptList.append((rowArray[0], rowArray[1]))
        elif flag == 3:
            # 开始写入
            # 第9行开始, C:内容 D:禅道编号, 空格分隔
            rowArray = lineContent.split(" ")
            if (len(rowArray)) == 3:
                # 没有禅道号的, (人员|内容, "")
                contentList.append((rowArray[1] + "|" + rowArray[2], ""))
            elif len(rowArray) > 3:
                # (人员|内容, 禅道号)
                contentList.append((rowArray[2] + "|" + rowArray[3], rowArray[1]))
            startRow = startRow + 1
    result = {"content": contentList, "dept": deptList}
    return result


if __name__ == '__main__':
    x = find("PAYZJ", "V_4_1_0_2")
    print(x)
