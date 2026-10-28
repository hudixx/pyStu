"""选修 B2 第 4 课参考答案。题 1、题 2 都过。题 3 写在下面。选修 B2 结束。

跑出来是：
没加载 InvalidRequestError
selectin 买牛奶
joined 买牛奶

关系是 lazy="raise"。没写 options 就点订单，接住了 InvalidRequestError。
selectinload 读到了「买牛奶」。多写的 joinedload 也读到了，题目没要求，结果是对的。

打印写在 with 外面。这次还能读，是因为加载发生在会话关掉之前，
订单已经在对象自己的内存里。这和第 1 课一样：加载过的值，脱离之后还能点。
如果没加载就在外面点，失败原因会变成 DetachedInstanceError，不再是 InvalidRequestError。
示例把打印放在 with 里面，点的时候会话还开着。

event 导入了没有用。titles_of 定义了没有调用。删掉不影响这三行。

题 3：
- lazy="raise" 用来让漏加载立刻失败。
  点到没在这次查询里声明的关系，不会再悄悄补一条 SELECT。
  对照关掉 Open Session In View 之后，忘了加载就让它失败，而不是在循环里变成 N+1。
- joinedload 是一条 JOIN。一个用户两张订单时，用户行会乘成两行，所以要 .unique()。
  selectinload 是两条：先查用户，再用 IN 查订单。用户那条查询的行数不变。
  集合常用 selectinload，多对一常用 joinedload。
  两种都只作用于这一次查询，不改类上的 lazy="raise"。
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
    """订单必须在查询时声明要加载。"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    orders: Mapped[list[Order]] = relationship(back_populates="user", lazy="raise")


class Order(Base):
    """一张订单。"""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(20))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="orders")


def main() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(User(name="hudi", orders=[Order(title="买牛奶")]))
        session.commit()

    with Session(engine) as session:
        user = session.scalars(select(User)).one()
        try:
            user.orders  # 没写 options。raise 不允许再补一条 SELECT。
        except InvalidRequestError:
            print("没加载 InvalidRequestError")

    with Session(engine) as session:
        user = session.scalars(
            select(User).options(selectinload(User.orders))
        ).one()
        # 会话还开着再点。订单已经由第二条 IN 查询取来。
        print("selectin", user.orders[0].title)

    with Session(engine) as session:
        user = session.scalars(
            select(User).options(joinedload(User.orders))
        ).unique().one()
        print("joined", user.orders[0].title)

    engine.dispose()


if __name__ == "__main__":
    main()
