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

# 添加运行脚本
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)