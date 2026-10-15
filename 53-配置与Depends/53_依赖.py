"""第 53 课示例：一个请求一个 Session。请求结束就提交并关闭。

对照：配置来自环境，不写死在代码里。Session 的生命周期跟这一次请求走，不是全局一个用到底。
"""

from __future__ import annotations

import os
from collections.abc import Iterator

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40))


class TodoIn(BaseModel):
    """请求体。空标题在进路由之前就 422。"""

    title: str = Field(min_length=1, max_length=40)


def make_engine():
    """内存库，但所有连接共用同一块。

    默认的 :memory: 每个连接各有一块库，建的表别的连接看不见。
    StaticPool 固定一条连接，TestClient 里的多次请求才能看见同一张表。
    """
    url = os.environ.get("DATABASE_URL", "sqlite:///:memory:")
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


engine = make_engine()
app = FastAPI(title="第 53 课")


def get_session() -> Iterator[Session]:
    """Depends 会调用这个生成器。yield 之前是请求开始，yield 之后是请求结束。

    成功才 commit。出了异常就 rollback。最后一定 close。
    """
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
    """普通 def。里面没有 await。对照 @PostMapping，参数上的 Depends 像方法参数上的注入。"""
    row = Todo(title=body.title)
    session.add(row)
    session.flush()  # 让数据库填上 id。commit 要等请求结束，由 get_session 做。
    return {"id": row.id, "title": row.title}


@app.get("/todos")
def list_todos(session: Session = Depends(get_session)) -> list[dict]:
    rows = session.scalars(select(Todo)).all()
    return [{"id": row.id, "title": row.title} for row in rows]


def main() -> None:
    client = TestClient(app)
    created = client.post("/todos", json={"title": "买牛奶"})
    print("创建", created.status_code, created.json())
    listed = client.get("/todos")
    print("列表", listed.status_code, listed.json())
    engine.dispose()


if __name__ == "__main__":
    main()
