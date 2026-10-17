from __future__ import annotations

import os
from typing import Iterator

from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass

class Todo(Base):
    __tablename__ = 'todos'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40))

class TodoIn(BaseModel):
    title: str = Field(min_length=1, max_length=40)

def make_engine():
    url = os.environ.get("DATABASE_URL", "sqlite:///:memory:")
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    return engine

engine = make_engine()
app = FastAPI(title="53练习")

def get_session() -> Iterator[Session]:
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.post("/todos")
def create_todo(body: TodoIn, session: Session = Depends(get_session)) -> dict:
    row = Todo(title=body.title)
    session.add(row)
    session.flush()
    return {"id": row.id, "title": row.title}

@app.get("/todos")
def list_todos(session: Session = Depends(get_session)) -> list[dict]:
    rows = session.scalars(select(Todo)).all()
    return [{"id": row.id, "title": row.title} for row in rows]

def main() -> None:
    client =TestClient(app)
    created = client.post("/todos", json={"title": "买牛奶"})
    print("创建", created.status_code, created.json())

    created = client.post("/todos", json={"title": "买豆浆"})
    print("创建", created.status_code, created.json())

    listed = client.get("/todos")
    print("列表", listed.status_code, listed.json())
    engine.dispose()

if __name__ == "__main__":
    main()

#  题3不知道，请在参考答案的注释中个给出