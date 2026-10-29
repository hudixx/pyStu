from __future__ import annotations

import pytest
import asyncio

from sqlalchemy import  create_engine, String, event, func, select
from sqlalchemy.orm import Mapped,mapped_column, Session, DeclarativeBase
from sqlalchemy.pool import StaticPool

class Base(DeclarativeBase):
    """实体根"""

class Todo(Base):
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40))

@pytest.fixture(scope="module")
def engine():
    bound = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(bound, "connect")
    def do_connect(dbapi_connection, connection_record) -> None:
        dbapi_connection.isolation_level = None

    @event.listens_for(bound, "begin")
    def do_begin(conn) -> None:
        conn.exec_driver_sql("BEGIN")
    Base.metadata.create_all(bound)
    yield bound
    bound.dispose()

@pytest.fixture
def session(engine):
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

@pytest.mark.asyncio # 这一行在这里不加也行，因为pytest.ini 写了 asyncio_mode = auto
async def test_tick() -> None:
    await asyncio.sleep(0)
    assert True

#  题3不知道，请在参考答案的注释中个给出