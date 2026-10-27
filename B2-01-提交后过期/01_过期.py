"""选修 B2 第 1 课：commit 之后属性过期。重新加载过的值会留下，没加载过的再点会脱离。

对照 JPA：提交后持久化上下文里的字段过期。
会话还没关时再点名字，会再查一次。对照还在 EntityManager 里，可以 refresh。
这份值加载进对象之后，with 结束仍能读到它。
从没在提交后再点过的字段，会话关了再点，就是 DetachedInstanceError。
对照没初始化的懒字段，在 EntityManager 关了之后再点。
"""

from __future__ import annotations

from sqlalchemy import String, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.orm.exc import DetachedInstanceError


class Base(DeclarativeBase):
    """实体根。这一课只有一张用户表。"""


class User(Base):
    """一行用户。本课关心的是提交之后这个对象还能不能点。"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40))


def count_selects(engine, work) -> int:
    """跑 work 期间数 SELECT。插入和建表不算。"""

    seen = {"n": 0}

    def before(conn, cursor, statement, parameters, context, executemany) -> None:
        # 只数查询。commit 本身通常不发 SELECT。
        if statement.lstrip().upper().startswith("SELECT"):
            seen["n"] += 1

    event.listen(engine, "before_cursor_execute", before)
    try:
        work()
    finally:
        event.remove(engine, "before_cursor_execute", before)
    return seen["n"]


def main() -> None:
    # 这一课只有一个会话，内存库就够。进程结束，库就没了。
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    loaded: User
    untouched: User
    with Session(engine) as session:
        loaded = User(name="hudi")
        untouched = User(name="li")
        session.add_all([loaded, untouched])
        session.commit()  # 默认 expire_on_commit=True。两个对象的名字都过期了。

        def read_name() -> None:
            # 会话还开着。过期不是「没了」，是「再点就再查一次」。
            print("提交后还在会话里", loaded.name)

        selects = count_selects(engine, read_name)
        print("这条读取", selects)  # 预期 1。这一次 SELECT 是过期之后的重新加载。
        # untouched.name 在提交之后没有再点。它一直是过期的。

    # 关掉之前已经重新加载过。脱离之后，这个字段还在对象自己的内存里。
    print("已经加载过", loaded.name)
    try:
        # 过期的字段加上已经脱离的对象，没有会话可以再查，于是失败。
        print(untouched.name)
    except DetachedInstanceError:
        print("没加载过 DetachedInstanceError")
    engine.dispose()


if __name__ == "__main__":
    main()
