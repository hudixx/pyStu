"""选修 B2 第 2 课：flush 把 SQL 发出去，commit 才让别的会话看见。

对照 EntityManager.flush 和事务 commit。
同一个会话里，flush 之后已经查得到。别的连接还在看上一次提交。
这里用临时文件库，是为了有两条真正的连接。用完就删，不留 db 文件。
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from sqlalchemy import String, create_engine, event, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    """实体根。"""


class Todo(Base):
    """一行待办。本课关心的是这一行谁能看见。"""

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40))


def count_todos(session: Session) -> int:
    """数已经能查到的行。scalar 取出那一个整数。"""

    found = session.scalar(select(func.count()).select_from(Todo))
    return found or 0


def main() -> None:
    # 内存库的每条连接各有一块库，没法演示「别的连接看不见」。
    # 临时文件才能让两个 Session 连到同一份数据。WAL 让读不至于被写锁住。
    fd, name = tempfile.mkstemp(suffix=".sqlite3")
    os.close(fd)
    path = Path(name)
    engine = create_engine(
        "sqlite:///" + path.as_posix(),
        connect_args={"check_same_thread": False},
    )

    def enable_wal(dbapi_conn, connection_record) -> None:
        # 写事务还开着时，另一条连接仍能读到上一次提交。读不到还没提交的那一行。
        dbapi_conn.execute("PRAGMA journal_mode=WAL")

    event.listen(engine, "connect", enable_wal)
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as first:
            first.add(Todo(title="买牛奶"))
            first.flush()  # INSERT 已经发到这条连接上。事务还没提交。
            print("flush 后同一个会话", count_todos(first))
            with Session(engine) as second:
                # 另一条连接。它看不见 first 还没提交的插入。
                print("flush 后别的会话", count_todos(second))
            first.commit()
        with Session(engine) as third:
            print("commit 后别的会话", count_todos(third))
    finally:
        engine.dispose()  # 先放开文件，Windows 上才能删掉。
        path.unlink(missing_ok=True)
        # WAL 模式会在旁边留下这两个文件。库删了，它们也删掉。
        Path(str(path) + "-wal").unlink(missing_ok=True)
        Path(str(path) + "-shm").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
