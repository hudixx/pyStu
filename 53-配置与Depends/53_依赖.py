"""第 53 课示例：一个请求一个 Session。请求结束就提交并关闭。

对照：配置来自环境，不写死在代码里。Session 的生命周期跟这一次请求走，不是全局一个用到底。
"""

from __future__ import annotations

import os  # 读 DATABASE_URL。对照 System.getenv，不要把连接串写死。
# Iterator 是生成器的标注。对照一个会分两次把控制权交回来的方法，不是返回 List。
from collections.abc import Iterator

# Depends：参数上的标记，告诉 FastAPI「这个值请调用某个函数来造」。对照方法参数上的注入。
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient  # 进程内客户端，不占端口。对照 MockMvc。
from pydantic import BaseModel, Field  # 请求体。空标题在进函数之前就 422。
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
# StaticPool：连接池里永远是同一条连接。内存库才不会「每次请求各看见一块空库」。
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    # 实体根。create_all 看的是它的 metadata。pass 表示类体没有自己的字段。
    pass


class Todo(Base):
    """和前两课同一张表。本课的新东西是：谁来开 Session、何时 commit。"""

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)  # SQLite 自己填。flush 之后才能从对象上读到。
    title: Mapped[str] = mapped_column(String(40))


class TodoIn(BaseModel):
    """请求体。空标题在进路由之前就 422。

    这是 pydantic，不是 SQLAlchemy。对照 @RequestBody 上的 @NotBlank @Size，进 Controller 之前就校验。
    """

    title: str = Field(min_length=1, max_length=40)  # 缺字段、""、超过 40 都是 422。路由函数不会跑。


def make_engine():
    """内存库，但所有连接共用同一块。

    默认的 :memory: 每个连接各有一块库，建的表别的连接看不见。
    StaticPool 固定一条连接，TestClient 里的多次请求才能看见同一张表。
    """
    # 没有环境变量就用内存库。生产把 DATABASE_URL 设成文件或别的库，代码不用改。
    url = os.environ.get("DATABASE_URL", "sqlite:///:memory:")
    engine = create_engine(
        url,
        # SQLite 默认不允许连接被另一个线程使用。TestClient 可能换线程，所以关掉这道检查。
        # 这是 SQLite 演示用的。换到 PostgreSQL 不要抄这个参数。
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # 池里只有一条连接，:memory: 才是同一块库。
    )
    # 演示才在造引擎时建表。生产用第 52 课的迁移，启动时 create_all 不会改已经存在的列。
    Base.metadata.create_all(engine)
    return engine


# 这两行在 import 本文件时就执行。对照静态初始化：进程里一份引擎、一份 FastAPI 应用。
engine = make_engine()
app = FastAPI(title="第 53 课")  # title 会出现在自动生成的 /docs 上。


def get_session() -> Iterator[Session]:
    """Depends 会调用这个生成器。yield 之前是请求开始，yield 之后是请求结束。

    成功才 commit。出了异常就 rollback。最后一定 close。
    对照包住 Controller 的 @Transactional：方法正常返回才提交，抛了就回滚，最后关 EntityManager。
    """
    session = Session(engine)  # 这一次请求专属。不要放到模块顶上当全局 Session 用到底。
    try:
        yield session  # 把 Session 交给路由函数。路由 return 之后，才从这一行继续往下。
        session.commit()  # 路由没抛异常，才提交。对照事务方法正常结束。
    except Exception:
        session.rollback()  # 路由里的异常会从 yield 那一行抛进这里。先回滚。
        raise  # 不带参数的 raise：把原来的异常原样再抛出去。对照 catch 里 rollback 后再 throw。
    finally:
        session.close()  # 提交或回滚之后都要关。对照 finally 里 em.close()。


@app.post("/todos")
def create_todo(body: TodoIn, session: Session = Depends(get_session)) -> dict:
    """普通 def。里面没有 await。对照 @PostMapping，参数上的 Depends 像方法参数上的注入。

    = Depends(...) 不是「现在就调用 get_session」。它只是一个标记，FastAPI 在每次请求时才调用。
    对照 Spring 看到参数类型就去容器里拿 Bean，你不会在方法签名里自己 new。
    """
    row = Todo(title=body.title)  # 此时还没有 id。主键要等数据库填。
    session.add(row)  # 放进这次请求的会话。对照 em.persist。
    session.flush()  # 把 INSERT 发到库，让数据库填上 id。commit 要等请求结束，由 get_session 做。
    # 现在 row.id 已经有值，可以放进响应。如果等 commit 才读，这个函数已经 return 了。
    return {"id": row.id, "title": row.title}


@app.get("/todos")
def list_todos(session: Session = Depends(get_session)) -> list[dict]:
    """另一次请求，另一个 Session。能看见上一笔，是因为上一笔已经 commit，不是因为 Session 是全局的。"""
    rows = session.scalars(select(Todo)).all()  # 执行查询，得到 Todo 对象的列表。
    # 列表推导：每行收成一个 dict。对照 stream.map(...).toList()。不要直接 return 实体。
    # 直接返回 Todo，FastAPI 不知道怎么把它写成 JSON，实体上也容易带上不该给前端的字段。
    return [{"id": row.id, "title": row.title} for row in rows]


def main() -> None:
    client = TestClient(app)  # 不 listen 端口。对照 MockMvc。
    # json= 会序列化并带上 Content-Type。空标题不会进 create_todo，这里的标题是合法的。
    created = client.post("/todos", json={"title": "买牛奶"})
    print("创建", created.status_code, created.json())  # 预期 200，JSON 里有数据库填的 id。
    listed = client.get("/todos")
    # 第二次请求是新的 Session。列表里仍有「买牛奶」，说明第一次在请求结束时 commit 了。
    print("列表", listed.status_code, listed.json())
    engine.dispose()  # 示例跑完就关池。TestClient 不会替你关 SQLAlchemy 的引擎。


if __name__ == "__main__":
    main()
