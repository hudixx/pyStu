"""选修 B2 第 3 课参考答案。题 1、题 2 都过。题 3 写在下面。

跑出来是：
不预加载 3
预加载 2

两个用户，各一张订单。先提交，再开始数 SELECT。建表和插入没有算进去。
不预加载是 1 条用户加 2 条订单，一共 3。selectinload 是 1 条用户加 1 条 IN，一共 2。

练习里插入函数名叫 send，参数名叫 func。能跑。插入更像 seed，参数更像 work，
避免和「发送」或者 sqlalchemy.func 搅在一起。

题 3：
- 循环里点 orders 会多出查询，是因为关系默认是点到才查。
  先查出两个用户，那是 1 条 SELECT。此时 orders 还没取来。
  user.orders 看起来像手里已经有的 list，第一次点它才发 SQL。
  两个用户就再发 2 条。1 加 N，这里 N 是 2。
  对照 @OneToMany(fetch = LAZY)。慢在往返次数，不在 ORM 这个名字。
- selectinload 不是把所有 SQL 并成一条。
  它先查用户，再用一条 WHERE user_id IN (...) 把这些人的订单一起取来。所以是 2 条。
  并成一条 JOIN 的是 joinedload。一对多时，用户行会按订单数乘开。
  selectin 让用户那条查询的行数保持不变，集合另查一次。
  它只作用于这一次查询，不改关系上的默认 lazy。
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
    orders: Mapped[list[Order]] = relationship(back_populates="user")


class Order(Base):
    """一张订单，属于一个用户。"""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(20))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="orders")


def count_selects(engine, work) -> int:
    """只数 work 里的 SELECT。"""

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
    """两个用户，各一张订单。提交并关掉，下一个会话不再留着这次的缓存。"""

    with Session(engine) as session:
        hudi = User(name="hudi", orders=[Order(title="买牛奶")])
        li = User(name="li", orders=[Order(title="买面包")])
        session.add_all([hudi, li])
        session.commit()


def titles_of(users: list[User]) -> None:
    """点到 orders 才会用到关系。不预加载时，每个用户一条 SELECT。"""

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
            users = list(
                session.scalars(select(User).options(selectinload(User.orders)))
            )
            titles_of(users)

    print("不预加载", count_selects(engine, lazy))
    print("预加载", count_selects(engine, preloaded))
    engine.dispose()


if __name__ == "__main__":
    main()
