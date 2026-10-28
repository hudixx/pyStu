"""选修 B3 第 4 课：测试里 commit 了，收尾仍把这次事务滚回去。

对照 @DataJpaTest：每个测试一个事务，结束回滚，不把「买牛奶」留到下一个测试。
库是 SQLite 内存库，整个文件共用一个引擎。每个测试自己开事务，结束 rollback。
async def 的测试不会自己跑。pytest-asyncio 负责把它放进事件循环。
"""

from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import String, create_engine, event, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    """实体根。"""


class Todo(Base):
    """一行待办。测试可以 commit，夹具结束时仍会滚掉。"""

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40))


@pytest.fixture(scope="module")
def engine():
    """这个文件共用一块内存库。表只建一次。"""

    # StaticPool 让这块 :memory: 在多次连接之间还是同一块库。
    bound = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(bound, "connect")
    def do_connect(dbapi_connection, connection_record) -> None:
        # SQLite 驱动会自己开事务。不关掉的话，测试里的 commit 会真的落库，外层 rollback 撤不掉。
        dbapi_connection.isolation_level = None

    @event.listens_for(bound, "begin")
    def do_begin(conn) -> None:
        # 改由 SQLAlchemy 发 BEGIN，外层事务才接得住测试里的保存点。
        conn.exec_driver_sql("BEGIN")

    Base.metadata.create_all(bound)
    yield bound
    bound.dispose()


@pytest.fixture
def session(engine):
    """每个测试一个外层事务。测试里的 commit 只提交保存点。"""

    connection = engine.connect()
    transaction = connection.begin()
    # create_savepoint：测试里 session.commit() 不会把外层事务提交掉。
    # 对照测试方法上的 @Transactional，方法结束回滚，不是真的落库。
    bound = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield bound
    bound.close()
    transaction.rollback()
    connection.close()


def test_add(session: Session) -> None:
    session.add(Todo(title="买牛奶"))
    session.commit()  # 提交的是保存点。外层事务还在。
    found = session.scalar(select(func.count()).select_from(Todo))
    assert found == 1


def test_clean(session: Session) -> None:
    # 上一个测试结束时外层事务回滚了。这张表又是空的。
    found = session.scalar(select(func.count()).select_from(Todo))
    assert found == 0


@pytest.mark.asyncio
async def test_tick() -> None:
    """async def 测试。没有 pytest-asyncio，pytest 不会执行这个协程。"""

    await asyncio.sleep(0)
    assert True
