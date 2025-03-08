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
    for sql in all_sql:
        if sql.strip() == "":
            continue
        # print(sql)
        if db.is_active is False:
            db = next(get_db())
        result = db.execute(sql)
        # print(result)
        print(result.fetchall())
        # print(result.keys())
        # print()
    # 数据填充报告模板
    template = obj.template
    # 返回报告
    # return crud.create_report(db=db, report=report)
    return ""