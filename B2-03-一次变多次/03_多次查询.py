"""选修 B2 第 3 课：循环里点关系，会变成 1 次加 N 次查询。

对照 Hibernate 的 N+1。先查出两个用户是 1 条 SELECT。
每个用户再点 orders，默认又各查一次，于是变成 3 条。
selectinload 先查出用户，再用一条 IN 查询把订单一起取来，是 2 条。
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, create_engine, event, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    selectinload,
)


class Base(DeclarativeBase):
    """实体根。"""


class User(Base):
    """一个用户，下面有多张订单。关系默认是点到才查。"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    # 不写 lazy，默认 select：第一次点 user.orders 才发 SQL。对照 @OneToMany(fetch = LAZY)。
    orders: Mapped[list[Order]] = relationship(back_populates="user")


class Order(Base):
    """一张订单，属于一个用户。"""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(20))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="orders")


def count_selects(engine, work) -> int:
    """只数 work 里的 SELECT。建表和插入不算，因为数之前已经提交过了。"""

    seen = {"n": 0}

    def before(conn, cursor, statement, parameters, context, executemany) -> None:
        if statement.lstrip().upper().startswith("SELECT"):
            seen["n"] += 1

    event.listen(engine, "before_cursor_execute", before)
    try:
        work()
    finally:
        event.remove(engine, "before_cursor_execute", before)
    return seen["n"]


def seed(engine) -> None:
    """两个用户，各一张订单。提交并关掉，避免下一个会话还留着缓存。"""

    with Session(engine) as session:
        hudi = User(name="hudi", orders=[Order(title="买牛奶")])
        li = User(name="li", orders=[Order(title="买面包")])
        session.add_all([hudi, li])
        session.commit()


def titles_of(users: list[User]) -> None:
    """点到 orders 才会用到关系。不预加载时，每次点都是一条新的 SELECT。"""

    for user in users:
        for order in user.orders:
            order.title


def main() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    seed(engine)

    def lazy() -> None:
        with Session(engine) as session:
            users = list(session.scalars(select(User)))
            titles_of(users)

    def preloaded() -> None:
        with Session(engine) as session:
            # options 只对这一次查询生效。不改关系上的默认 lazy。
            users = list(
                session.scalars(select(User).options(selectinload(User.orders)))
            )
            titles_of(users)

    print("不预加载", count_selects(engine, lazy))  # 1 条用户 + 2 条订单 = 3。
    print("预加载", count_selects(engine, preloaded))  # 1 条用户 + 1 条 IN = 2。
    engine.dispose()


if __name__ == "__main__":
    main()
