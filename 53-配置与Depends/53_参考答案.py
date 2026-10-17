"""第 53 课参考答案。题 1、题 2 都过。题 3 写在下面。

跑出来是：
创建 200 {'id': 1, 'title': '买牛奶'}
列表 200 [{'id': 1, 'title': '买牛奶'}]

POST 的状态码是 200，响应里有「买牛奶」。
GET 还能看见这一条。两次请求用的是同一块库，第一次请求结束时提交了。
Session 通过 Depends 交给路由，没有做成全局变量。
路由里只 flush，commit 在 get_session 的 yield 之后。

练习多插了一条「买豆浆」。列表里两条都在，说明提交是按请求走的，不算错。
client =TestClient(app) 等号两边少了空格。赋值要写成 client = TestClient(app)。
TestClient 从 starlette 导入，这次能跑。和教程对齐时用 fastapi.testclient。
StaticPool 从 sqlalchemy 顶层导入也能用。教程写的是 sqlalchemy.pool。

题 3：
- 不能做一个全局 Session，所有请求一起用。
  Session 是一次工作单元，不是连接池。对照一个 EntityManager，不是 DataSource。
  所有请求共用一个：A 还没提交，B 可能看见或一起改；A 回滚会把 B 还没提交的改动也撤掉。
  两个请求同时用，未提交的对象会串。
  引擎（连接池）可以是进程里一份。Session 跟这一次请求走，结束就 commit 并 close。
- 路由函数里提前 commit，后面的失败收不回来。
  commit 已经把这一行提交了。后面再抛错，get_session 里的 rollback
  只能回滚还没提交的部分，收不回已经 commit 的那一行。
  flush 只是让这次会话能读到数据库填上的 id。提交仍放在 yield 之后。
  对照一个 @Transactional 方法：中间自己 commit，后面抛异常时前面那笔已经落库。
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
    """实体根。create_all 看的是它的 metadata。"""

    pass


class Todo(Base):
    """一行待办。本课的新东西是谁来开 Session、何时 commit。"""

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)  # flush 之后才能从对象上读到。
    title: Mapped[str] = mapped_column(String(40))


class TodoIn(BaseModel):
    """请求体。空标题在进路由之前就是 422。这是 pydantic，不是 SQLAlchemy。"""

    title: str = Field(min_length=1, max_length=40)


def make_engine():
    """内存库，但所有连接共用同一块。否则每个连接各有一块空库。"""

    url = os.environ.get("DATABASE_URL", "sqlite:///:memory:")
    engine = create_engine(
        url,
        # TestClient 可能换线程。这是 SQLite 演示用的，换 PostgreSQL 不要抄。
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # 池里只有一条连接，:memory: 才是同一块库。
    )
    Base.metadata.create_all(engine)  # 演示才在这里建表。生产用迁移。
    return engine


engine = make_engine()  # 进程里一份引擎。不是一份 Session。
app = FastAPI(title="第 53 课")


def get_session() -> Iterator[Session]:
    """一次请求一个 Session。yield 之前打开，yield 之后提交或回滚，最后关闭。"""

    session = Session(engine)  # 这一次请求专属。不要放到模块顶上用到底。
    try:
        yield session  # 交给路由。路由 return 之后，才从这里继续。
        session.commit()  # 路由没抛异常才提交。
    except Exception:
        session.rollback()
        raise  # 原样再抛出去。不要在这里吞掉。
    finally:
        session.close()


@app.post("/todos")
def create_todo(body: TodoIn, session: Session = Depends(get_session)) -> dict:
    """Depends 是标记。FastAPI 在每次请求时才调用 get_session，不是定义函数时就调用。"""

    row = Todo(title=body.title)  # 此时还没有 id。
    session.add(row)
    session.flush()  # 发出 INSERT，让数据库填上 id。commit 仍等请求结束。
    return {"id": row.id, "title": row.title}


@app.get("/todos")
def list_todos(session: Session = Depends(get_session)) -> list[dict]:
    """另一次请求，另一个 Session。能看见上一笔，是因为上一笔已经 commit。"""

    rows = session.scalars(select(Todo)).all()
    return [{"id": row.id, "title": row.title} for row in rows]


def main() -> None:
    client = TestClient(app)  # 不占端口。
    created = client.post("/todos", json={"title": "买牛奶"})
    print("创建", created.status_code, created.json())
    listed = client.get("/todos")
    print("列表", listed.status_code, listed.json())
    engine.dispose()


if __name__ == "__main__":
    main()
