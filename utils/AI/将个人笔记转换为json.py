"""
批量将个人笔记转换为一个json文件
"""
import json
import orgparse
import os

def buildAllOrgmodePath(path, allFilePathList):
    dirs = os.listdir(path)
    for dir in dirs:
        fullPath = path + "/" + dir
        if dir == ".git" or dir == ".gitignore" or dir == "tmp.org":
           continue
        elif (os.path.isfile(fullPath)):
           allFilePathList.append(fullPath)
        else:
           buildAllOrgmodePath(fullPath, allFilePathList)

def parseOrg2Json(path):
    orgFile = orgparse.load(path)
    print(orgFile)


def parseAllOrg2Json(allFilePath):
    for p in allFilePath:
        parseOrg2Json(p)


if __name__ == '__main__':
    allFilePath = []
    # 递归获取所有文件路径
    buildAllOrgmodePath("/home/zhaozhiwei/Documents/notes", allFilePath)
    print(allFilePath)
    # 分别解析构建每个文件,转换为json, 合并转换结果，写入到一个文件中
    fullJson = parseAllOrg2Json(allFilePath)
    print(fullJson)

