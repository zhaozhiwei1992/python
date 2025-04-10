# !user/bin/python
# _*_ coding: utf-8 _*_
from fastapi import FastAPI, HTTPException, Request, Depends
from reports.router import router as reports_router
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

# 创建FastAPI应用
app = FastAPI()

# 包含报告模块的路由
app.include_router(reports_router, prefix="/reports", tags=["reports"])

# 新增SQL查询接口
@app.post("/buscommon/llm/querysql")
async def execute_sql(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        sql = data.get("sql")
        if not sql:
            raise HTTPException(status_code=400, detail="SQL statement is required")
        
        result = db.execute(text(sql)).fetchall()
        return [dict(row) for row in result]
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/buscommon/llm/queryMenu")
async def execute_sql(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        menuId = data.get("menu_id")
        sql = "select * from fasp_t_pubmenu where guid = '" + menuId + "'"
        result = db.execute(text(sql)).fetchall()
        arr = [dict(row) for row in result]
        menuObj = arr[0]
        # 获取菜单url
        url = menuObj.get("url")
        url += "&menuName=申报预算(代录)"
        obj = {"url": url}
        obj['menu_id'] = menuId
        obj['menu_name'] = "申报预算(代录)"
        suggested = [
            {'type': '1', 'value': '请输入预算编制项目'},
            {'type': '2', 'value': '请输入预算编制项目'},
            {'type': '3', 'value': '请输入预算编制项目'}
        ]
        obj['suggested'] = suggested
        obj['text'] = "好的，已经打开申报预算"
        obj['suggested_method'] = 'Ext.lt.bdg.addProAI'
        return obj
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))


# 添加运行脚本
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)