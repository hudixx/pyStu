"""第 51 课示例：一个事务里的两行，要么都在，要么都不在。

对照 @Transactional。方法中途抛异常，已经 persist 的那一行也会滚回去。
"""

from __future__ import annotations

from sqlalchemy import String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40))


def add_pair(engine, second: str) -> None:
    """两条插入在同一个事务里。second 为空就抛错，第一条也不留。"""
    with Session(engine) as session:
        # begin() 成功走完会 commit。里面抛异常会 rollback。对照一个 @Transactional 方法。
        with session.begin():
            session.add(Todo(title="买牛奶"))
            if second == "":
                # 在提交之前失败。不要先 commit 第一条，再插第二条。
                raise ValueError("标题为空")
            session.add(Todo(title=second))


def count_rows(engine) -> int:
    """新开一个会话来数。上一个事务已经结束，这里看到的是提交之后的结果。"""
    with Session(engine) as session:
        # func.count 是 SQL 的 COUNT(*)。scalar_one 取出那一个数字。
        return session.scalar(select(func.count()).select_from(Todo)) or 0


def main() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    try:
        add_pair(engine, "")
    except ValueError as exc:
        print("失败:", exc)
    print("失败后行数:", count_rows(engine))

    add_pair(engine, "买面包")
    print("成功后行数:", count_rows(engine))
    engine.dispose()


if __name__ == "__main__":
    main()
