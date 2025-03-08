from sqlalchemy.orm import Session
from sqlalchemy import text
from . import schemas

def create_report(db: Session, report: schemas.ReportCreate):
    extra = report.extra if report.extra else {}
    query = text("INSERT INTO reports (title, content, extra) VALUES (:title, :content, :extra) RETURNING id")
    result = db.execute(query, {"title": report.title, "content": report.content, "extra": extra})
    db.commit()
    report_id = result.scalar()
    return {"id": report_id, "title": report.title, "content": report.content, "extra": extra}

def get_reports(db: Session):
    query = text("SELECT id, title, content, extra FROM reports")
    results = db.execute(query).fetchall()
    return [{"id": row.id, "title": row.title, "content": row.content, "extra": row.extra} for row in results]

def get_report(db: Session, report_id: int):
    query = text("SELECT id, title, content, extra FROM reports WHERE id = :report_id")
    result = db.execute(query, {"report_id": report_id}).first()
    if result:
        return {"id": result.id, "title": result.title, "content": result.content, "extra": result.extra}
    return None

def update_report(db: Session, report_id: int, report: schemas.ReportCreate):
    extra = report.extra if report.extra else {}
    query = text("UPDATE reports SET title = :title, content = :content, extra = :extra WHERE id = :report_id")
    db.execute(query, {"title": report.title, "content": report.content, "extra": extra, "report_id": report_id})
    db.commit()
    return {"id": report_id, "title": report.title, "content": report.content, "extra": extra}

def delete_report(db: Session, report_id: int):
    query = text("DELETE FROM reports WHERE id = :report_id")
    db.execute(query, {"report_id": report_id})
    db.commit()
    return {"id": report_id}