"""选修 B2 第 4 课：没声明要加载，就不要在后面偷偷查。

lazy="raise" 对照一条你不允许临时再查的映射。
点到没加载的关系，立刻失败，而不是在循环里补 N 条 SQL。
selectinload 是两条查询。joinedload 是一条 JOIN。这一次查询写清楚用哪一种。
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    joinedload,
    mapped_column,
    relationship,
    selectinload,
)


class Base(DeclarativeBase):
    """实体根。"""


class User(Base):
    """订单必须在查询时声明要加载。默认 raise，点到没加载的集合就失败。"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    # raise：禁止点到才查。对照关掉 Open Session In View 之后，漏了加载就让它失败。
    orders: Mapped[list[Order]] = relationship(back_populates="user", lazy="raise")


class Order(Base):
    """一张订单。"""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(20))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="orders")


def seed(engine) -> None:
    with Session(engine) as session:
        session.add(User(name="hudi", orders=[Order(title="买牛奶")]))
        session.commit()


def main() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    seed(engine)

    with Session(engine) as session:
        user = session.scalars(select(User)).one()
        try:
            # 查询时没写 options。关系是 raise，这里不能再补一条 SELECT。
            user.orders
        except InvalidRequestError:
            print("没加载 InvalidRequestError")

    with Session(engine) as session:
        user = session.scalars(
            select(User).options(selectinload(User.orders))
        ).one()
        # 第二条 SQL 用 IN 把这个用户的订单取来。集合已经在手里，点它不再查。
        print("selectin", user.orders[0].title)

    with Session(engine) as session:
        # JOIN 把用户和订单放在同一条 SQL 里。一行用户配一行订单时，结果行会重复。
        # unique() 按主键把重复的用户收成一个。对照 DISTINCT 根实体，不是把订单去重没了。
        user = session.scalars(
            select(User).options(joinedload(User.orders))
        ).unique().one()
        print("joined", user.orders[0].title)

    engine.dispose()


if __name__ == "__main__":
    main()
