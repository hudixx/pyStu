"""选修 B3 第 4 课参考答案。题 1 过了。题 2 在本课目录里过了，标记没写。题 3 写在下面。

本课目录一起跑是 6 passed。示例 3 个，练习 3 个。只跑本文件是 3 passed。

插入「买牛奶」并 commit 之后，行数是 1。下一个测试行数是 0。
外层事务在夹具收尾时 rollback。测试里的 commit 提交的是保存点，不是那一层。

SQLite 那两行抄上了：connect 时 isolation_level = None，begin 时自己发 BEGIN。
没有这两行，驱动会自己把 commit 落库，下一个测试会看到 1。

async def 测试里 await asyncio.sleep(0)，然后 assert True。
没有加 @pytest.mark.asyncio。本课 pytest.ini 写了 asyncio_mode = auto，所以没标记也跑了。
把模式改成 strict 之后，这一条失败，报告是 async def functions are not natively supported。
题目要求加上标记。

import 后面多了一个空格：import  create_engine。
Mapped,mapped_column 逗号后面少了一个空格。
顶层函数之间少了一行空行。本课 ruff 没报，不影响测试。

题 3：
- 下一个测试是 0 行，因为夹具先开了一层外层事务，Session 用 create_savepoint。
  测试里的 commit 只提交保存点。测试结束，夹具对那层外层事务 rollback，插入就没了。
  下一个测试是新的会话、新的外层事务，表又是空的。不是每个测试换了一个新库。
- pytest 调用 async def，拿到的是一个还没执行的协程，不会自己 await。
  sleep 不会发生，断言也不会跑到。pytest-asyncio 把它放进事件循环再 await。
  标记是告诉插件「这一条交给你」。auto 是本目录的配置替你做了这件事。
  不要在同步测试里再包一层 asyncio.run 来假装。
"""

from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import String, create_engine, event, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    """实体根。create_all 看的是它的 metadata。"""


class Todo(Base):
    """一行待办。测试可以 commit，夹具结束时仍会滚掉。"""

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40))


@pytest.fixture(scope="module")
def engine():
    """这个文件共用一块内存库。表只建一次。"""

    bound = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(bound, "connect")
    def do_connect(dbapi_connection, connection_record) -> None:
        # 关掉驱动自己开的事务。不关的话，测试里的 commit 会真的落库。
        dbapi_connection.isolation_level = None

    @event.listens_for(bound, "begin")
    def do_begin(conn) -> None:
        # 改由 SQLAlchemy 发 BEGIN，外层 rollback 才撤得掉保存点里的插入。
        conn.exec_driver_sql("BEGIN")

    Base.metadata.create_all(bound)
    yield bound
    bound.dispose()


@pytest.fixture
def session(engine):
    """每个测试一个外层事务。测试里的 commit 只提交保存点。"""

    connection = engine.connect()
    transaction = connection.begin()
    bound = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield bound
    bound.close()
    transaction.rollback()
    connection.close()


def test_add(session: Session) -> None:
    session.add(Todo(title="买牛奶"))
    session.commit()
    found = session.scalar(select(func.count()).select_from(Todo))
    assert found == 1


def test_clean(session: Session) -> None:
    found = session.scalar(select(func.count()).select_from(Todo))
    assert found == 0


@pytest.mark.asyncio
async def test_tick() -> None:
    await asyncio.sleep(0)
    assert True
