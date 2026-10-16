"""
1. 安装依赖
pip install fastapi uvicorn openpyxl
2. 启动
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
3. 调用示例（curl）
curl -X POST http://localhost:8000/api/ai-forms/field-options/query \
  -H "Content-Type: application/json" \
  -d '{"formCode":"TESTSCHEMA","fieldCode":"travelType"}'
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Form Field Options Stub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- 模拟从 Excel 加载的字典（实际可换成 pd.read_excel） ----------
FIELD_OPTIONS = {
    # 差旅类型 travelType
    ("TESTSCHEMA", "travelType"): [
        {"value": "1", "label": "公务出差"},
        {"value": "2", "label": "会议"},
        {"value": "3", "label": "培训"},
        {"value": "4", "label": "驻点"},
        {"value": "5", "label": "公务-公务"},
        {"value": "6", "label": "市内出差"},
    ],
    # 出差人员 travelPersonId（截取部分示例，全量照抄 data_id + name 即可）
    ("TESTSCHEMA", "travelPersonId"): [
        {"value": "1838859627928700001", "label": "核算管理员"},
        {"value": "1910203461338509314", "label": "测试用户"},
        {"value": "1838464373685751809", "label": "财务发起"},
        {"value": "1840303351317663745", "label": "省本级业务用户"},
        {"value": "1848601368026157057", "label": "刘方芳"},
        # ……其余人员按同样格式追加
    ],
    # 经济分类 element08（政府收支科目，只放常用叶子节点）
    ("TESTSCHEMA", "element08"): [
        {"value": "30211", "label": "差旅费"},
        {"value": "30201", "label": "办公费"},
        {"value": "30215", "label": "会议费"},
        {"value": "30216", "label": "培训费"},
        {"value": "30217", "label": "公务接待费"},
        {"value": "30231", "label": "公务用车运行维护费"},
        {"value": "301", "label": "工资福利支出"},
        {"value": "302", "label": "商品和服务支出"},
        # ……完整树可按 LEVEL_NO / IS_LEAF 过滤后全量灌入
    ],
}
# -----------------------------------------------------------------------


@app.post("/api/ai-forms/field-options/query")
async def get_form_field_options(body: dict):
    """
    严格对齐你给的 MCP / AI-Form 工具契约：
    requestBody: { formCode, fieldCode }
    返回: { options: [{value, label}] }
    """
    form_code = body.get("formCode", "")
    field_code = body.get("fieldCode", "")

    key = (form_code, field_code)
    print("请求key", key)
    options = FIELD_OPTIONS.get(key)

    if options is None:
        # 没配的字段返回空数组，而不是 404，避免 AI 工具误判失败
        print("无法返回")
        return {"options": []}

    return {"options": options}


@app.get("/health")
def health():
    return {"ok": True}
