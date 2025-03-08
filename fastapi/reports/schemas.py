from pydantic import BaseModel


class ReportCreate(BaseModel):
    sql: str
    template: str