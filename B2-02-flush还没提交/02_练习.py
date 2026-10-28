from __future__ import annotations

import os
import tempfile
from pathlib import Path

from sqlalchemy import create_engine, String, event, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


class Base(DeclarativeBase):
    """占位"""

class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40))

def count_todos(session: Session) -> int:
    fount = session.scalar(select(func.count()).select_from(Todo))
    return fount or 0

def main() -> None:
    fd, name = tempfile.mkstemp(suffix=".sqlite3")
    os.close(fd)
    path = Path(name)
    engine = create_engine(
        "sqlite:///" + path.as_posix(),
        connect_args={"check_same_thread": False},
    )

    def enable_wal(dbapi_conn, connection_record) -> None:
        dbapi_conn.execute("PRAGMA journal_mode=WAL")

    event.listen(engine, "connect", enable_wal)
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as first:
            first.add(Todo(title="买牛奶"))
            first.flush()
            print("flush 后同一个会话", count_todos(first))
            with Session(engine) as second:
                print("flush 后别的会话", count_todos(second))
            first.commit()
            with Session(engine) as third:
                print("commit 后别的会话", count_todos(third))
    finally:
        engine.dispose()
        path.unlink(missing_ok=True)
        Path(str(path) + "-wal").unlink(missing_ok=True)
        Path(str(path) + "-shm").unlink(missing_ok=True)

if __name__ == "__main__":
    main()

#  题3不知道，请在参考答案的注释中个给出