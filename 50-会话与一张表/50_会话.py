"""第 50 课示例：待办在表里，不在内存列表里。

对照 JPA：Todo 是实体，Session 是一次工作单元，commit 之后才算写入。
数据库用 SQLite 内存库。进程结束，表就没了。本课不留 db 文件。
"""

from __future__ import annotations

from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    """所有实体的共同基类。对照 JPA 里带 @Entity 的类要被扫描到的那个根。"""


class Todo(Base):
    """一张表。类属性是列，不是普通的实例字段。"""

    __tablename__ = "todos"  # 表名。类名 Todo 不会自动变成表名。

    id: Mapped[int] = mapped_column(primary_key=True)  # 主键。SQLite 会自己填整数。
    title: Mapped[str] = mapped_column(String(40))  # 对照 @Column(length = 40)。


def main() -> None:
    # sqlite:///:memory: 是一块只在这个进程里的库。对照 H2 的内存模式，不是 MySQL。
    engine = create_engine("sqlite:///:memory:")
    # 按实体建表。教学演示用这一行。生产环境用第 52 课的迁移，不要靠启动时建表。
    Base.metadata.create_all(engine)

    # with 结束时关闭 Session。对照 EntityManager 用完要 close，不要做成永远不关的 static 字段。
    with Session(engine) as session:
        session.add(Todo(title="买牛奶"))  # 先放进会话，这时还没提交。
        session.commit()  # 提交之后，别的会话才能查到。
        # select 是查询语句。scalars() 取出 Todo 对象，而不是一行行的元组。
        rows = session.scalars(select(Todo)).all()
        for row in rows:
            print(row.id, row.title)

    engine.dispose()  # 关掉连接池。内存库随之丢掉。


if __name__ == "__main__":
    main()
