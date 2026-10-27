"""选修 B2 第 2 课：flush 把 SQL 发出去，commit 才让别的会话看见。

对照 EntityManager.flush 和事务 commit。
同一个会话里，flush 之后已经查得到。别的连接还在看上一次提交。
这里用临时文件库，是为了有两条真正的连接。用完就删，不留 db 文件。
"""

from __future__ import annotations

import os  # os.close：关掉 mkstemp 打开的那个文件句柄。不关的话，Windows 上后面可能删不掉。
import tempfile  # 在系统临时目录造一个空文件。对照 Files.createTempFile，但多返回一个整数句柄。
from pathlib import Path  # 路径对象。as_posix、unlink 都在它上面。对照 java.nio.file.Path。

# func.count 是 SQL 的 COUNT。select 是写好但还没执行的查询。event 用来在新连接上开 WAL。
from sqlalchemy import String, create_engine, event, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    """实体根。create_all 看的是它的 metadata。"""


class Todo(Base):
    """一行待办。本课关心的是这一行谁能看见。"""

    __tablename__ = "todos"  # 表名。对照 @Table(name = "todos")。

    id: Mapped[int] = mapped_column(primary_key=True)  # 主键。SQLite 自己填。
    title: Mapped[str] = mapped_column(String(40))  # 最长 40 的字符串列。


def count_todos(session: Session) -> int:
    """数已经能查到的行。scalar 取出那一个整数。

    session 标成 Session：调用时要传入一个打开的会话。这个函数自己不开关会话。
    """

    # select(func.count()) 是 SELECT COUNT(*)。select_from(Todo) 指定从哪张表数。
    # scalar() 取第一行第一列，查不到时是 None。对照 getSingleResult，但 None 不抛异常。
    found = session.scalar(select(func.count()).select_from(Todo))
    # or：左边是 None 或 0 时用右边的 0。None or 0 得到 0。有行时 found 是正整数，原样返回。
    # 对照 found == null ? 0 : found。0 本身也是假值，所以 COUNT 为 0 时也会走到 0，结果一样。
    return found or 0


def main() -> None:
    # 内存库的每条连接各有一块库，没法演示「别的连接看不见」。
    # 临时文件才能让两个 Session 连到同一份数据。WAL 让读不至于被写锁住。
    # mkstemp 返回两个值：fd 是已经打开的整数句柄，name 是路径字符串。对照一次 return 一个 Pair。
    # suffix 让文件名以 .sqlite3 结尾。这只是名字，SQLite 不靠后缀认文件。
    fd, name = tempfile.mkstemp(suffix=".sqlite3")
    os.close(fd)  # 句柄不用，马上关。后面 SQLAlchemy 会自己打开这个路径。
    path = Path(name)  # 把字符串包成 Path，才能用 as_posix 和 unlink。
    engine = create_engine(
        # as_posix() 把路径里的反斜杠换成正斜杠。SQLite 的 URL 要用 /，Windows 的 \ 会把 URL 弄断。
        # "sqlite:///" 三个斜杠后面直接跟绝对路径。用 + 拼接字符串。对照字符串相加，不是 Path 的 /。
        "sqlite:///" + path.as_posix(),
        # SQLite 默认不允许别的线程用这条连接。两个 Session 可能不在同一个线程，所以关掉这道检查。
        # 这是演示用的。换 PostgreSQL 不要抄这个参数。
        connect_args={"check_same_thread": False},
    )

    def enable_wal(dbapi_conn, connection_record) -> None:
        # 嵌套函数。每条新的数据库连接建立时，SQLAlchemy 会调用它。第二个参数本课不用。
        # 写事务还开着时，另一条连接仍能读到上一次提交。读不到还没提交的那一行。
        # execute 这里是底层驱动的方法，不是 Session 的。PRAGMA 是 SQLite 自己的设置语句。
        dbapi_conn.execute("PRAGMA journal_mode=WAL")

    # "connect" 事件：连接刚建好、还没拿去跑业务 SQL 时触发。对照连接池里每取出一条新连接做一次初始化。
    event.listen(engine, "connect", enable_wal)
    Base.metadata.create_all(engine)  # 建表。这时就会新建连接，于是 enable_wal 会跑到。
    try:
        with Session(engine) as first:
            first.add(Todo(title="买牛奶"))  # 只放进这个会话。还没发 INSERT。
            first.flush()  # INSERT 已经发到这条连接上。事务还没提交。对照 em.flush()，不是 commit。
            print("flush 后同一个会话", count_todos(first))  # 同一个会话看得到自己 flush 出去的行。预期 1。
            with Session(engine) as second:
                # 另一条连接。它看不见 first 还没提交的插入。嵌套的 with 先结束，second 先关。
                print("flush 后别的会话", count_todos(second))  # 预期 0。
            first.commit()  # 提交之后，别的连接才能看见。对照事务 commit。
        # 外层 with 结束，first 关了。提交已经完成，不依赖这个会话还开着。
        with Session(engine) as third:
            print("commit 后别的会话", count_todos(third))  # 新会话。预期 1。
    finally:
        engine.dispose()  # 先放开文件，Windows 上才能删掉。对照先关连接池，再删文件。
        path.unlink(missing_ok=True)  # 删除临时库。missing_ok=True：已经不在也不抛。对照 deleteIfExists。
        # WAL 模式会在旁边留下这两个文件。库删了，它们也删掉。
        # str(path) 把 Path 变回字符串，再用 + 接上后缀。这是文件名拼接，不是 SQL。
        Path(str(path) + "-wal").unlink(missing_ok=True)
        Path(str(path) + "-shm").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
