from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from . import schemas

router = APIRouter()

# 创建报告
@router.post("/buscommon/report")
async def create_report(obj: schemas.ReportCreate, db: Session = Depends(get_db)):
    # 解析sql参数, 查询数据
    # print(obj)
    all_sql = obj.sql.replace("\n", "").split(";")
    resultDatas = []
    for sql in all_sql:
        if sql.strip() == "":
            continue
        # print(sql)
        if db.is_active is False:
            db = next(get_db())
        result = db.execute(sql)
        # print(result)
        # print(result.fetchall())
        for row in result:
            colRow = dict(zip([str(col).lower() for col in result.keys()], row))
            resultDatas.append(colRow)
    # 数据填充报告模板
    templateText = str(obj.template).split("表说明")[0]
    print(templateText)
    # 返回报告
    allObj = {}
    for dictRow in resultDatas:
        # 替换template
        # print(dictRow['year'])
        allObj.update(dictRow)
    print(allObj)
    templateText = templateText.format(**allObj)
    return templateText

@router.post("/buscommon/llm/queryMenu")
async def create_report(obj: schemas.ReportCreate, db: Session = Depends(get_db)):
    # 解析sql参数, 查询数据
    # print(obj)
    all_sql = obj.sql.replace("\n", "").split(";")
    resultDatas = []
    for sql in all_sql:
        if sql.strip() == "":
            continue
        # print(sql)
        if db.is_active is False:
            db = next(get_db())
        result = db.execute(sql)
        # print(result)
        # print(result.fetchall())
        for row in result:
            colRow = dict(zip([str(col).lower() for col in result.keys()], row))
            resultDatas.append(colRow)
    # 数据填充报告模板
    templateText = str(obj.template).split("表说明")[0]
    print(templateText)
    # 返回报告
    allObj = {}
    for dictRow in resultDatas:
        # 替换template
        # print(dictRow['year'])
        allObj.update(dictRow)
    print(allObj)
    templateText = templateText.format(**allObj)
    return templateText
