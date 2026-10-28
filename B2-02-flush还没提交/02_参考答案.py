"""选修 B2 第 2 课参考答案。题 1、题 2 都过。题 3 写在下面。

跑出来是：
flush 后同一个会话 1
flush 后别的会话 0
commit 后别的会话 1

临时文件库、WAL、跑完删除，都有。flush 之后同一个会话是 1，别的会话是 0。
commit 之后别的会话是 1。

练习里计数字写成了 fount。能跑，但看不出是 found。写成 found。
第三次会话写在 first 的 with 里面、commit 之后。first 还没关，但 third 是另一个 Session。
数到 1 是因为已经 commit，不是因为还待在同一个 with 里。
示例把第三个会话放在 with 结束之后，两边都算「别的会话」。

题 3：
- flush 把 INSERT 发到当前这条连接上，事务还没提交。
  commit 才结束这次事务，别的连接才能看见。
  对照 em.flush() 和事务 commit 不是同一步。
- 同一个会话查得到，只说明这行在它自己的事务里。
  别的会话还在看上一次提交，所以那时是 0。
  不能用「我这个会话查到了」代替「库已经对所有人提交了」。
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
    """数已经能查到的行。"""

    found = session.scalar(select(func.count()).select_from(Todo))
    return found or 0


def main() -> None:
    fd, name = tempfile.mkstemp(suffix=".sqlite3")
    os.close(fd)
    path = Path(name)
    engine = create_engine(
        "sqlite:///" + path.as_posix(),
        connect_args={"check_same_thread": False},
    )

    def enable_wal(dbapi_conn, connection_record) -> None:
        # 写事务还开着时，另一条连接仍能读到上一次提交。
        dbapi_conn.execute("PRAGMA journal_mode=WAL")

    event.listen(engine, "connect", enable_wal)
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as first:
            first.add(Todo(title="买牛奶"))
            first.flush()  # INSERT 已发出。事务还没提交。
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
