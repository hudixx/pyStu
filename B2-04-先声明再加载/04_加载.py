"""选修 B2 第 4 课：没声明要加载，就不要在后面偷偷查。

lazy="raise" 对照一条你不允许临时再查的映射。
点到没加载的关系，立刻失败，而不是在循环里补 N 条 SQL。
selectinload 是两条查询。joinedload 是一条 JOIN。这一次查询写清楚用哪一种。
"""

from __future__ import annotations

# ForeignKey 是库里的外键。select 是查询对象，调用 .options 之前还没执行。
from sqlalchemy import ForeignKey, String, create_engine, select
# InvalidRequestError：用法不被允许，比如点了一个标成 raise、却没预先加载的关系。不是「查不到数据」。
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    joinedload,  # 用 JOIN 把关系在同一条 SQL 里取来。结果行会按订单数变多。
    mapped_column,
    relationship,
    selectinload,  # 第二条 SQL，用 IN 把关系取来。用户那条查询的行数不会因为订单变多。
)


class Base(DeclarativeBase):
    """实体根。"""


class User(Base):
    """订单必须在查询时声明要加载。默认 raise，点到没加载的集合就失败。"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    # raise：禁止点到才查。对照关掉 Open Session In View 之后，漏了加载就让它失败。
    # lazy="raise" 是这个关系的默认策略。某一次查询仍可以用 options 声明「这次我要加载」。
    # list[Order] 能写在 Order 定义之前，是因为文件顶部把标注推迟求值了，这里不会立刻去找 Order。
    orders: Mapped[list[Order]] = relationship(back_populates="user", lazy="raise")


class Order(Base):
    """一张订单。"""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(20))
    # "users.id" 是表名.列名，不是类名。对照 @JoinColumn(name = "user_id") 指向那一列。
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # 这一边没写 lazy="raise"。本课只从用户去点订单，不从订单去点用户。
    user: Mapped[User] = relationship(back_populates="orders")


def seed(engine) -> None:
    """插入一个用户和一张订单，然后提交并关掉会话。后面的查询都是新会话。"""

    with Session(engine) as session:
        # orders=[...] 是只有一个元素的列表。构造时挂上订单，commit 时两行一起写入。
        session.add(User(name="hudi", orders=[Order(title="买牛奶")]))
        session.commit()


def main() -> None:
    engine = create_engine("sqlite:///:memory:")  # 内存库。对照 H2 内存模式。进程结束数据就没了。
    Base.metadata.create_all(engine)  # 建 users 和 orders。
    seed(engine)

    with Session(engine) as session:
        # scalars(...).one()：必须正好一行。0 行抛异常，多于 1 行也抛。对照 getSingleResult。
        # 查询没写 options，所以 orders 没被加载。
        user = session.scalars(select(User)).one()
        try:
            # 查询时没写 options。关系是 raise，这里不能再补一条 SELECT。
            # 单独写 user.orders：只是去读这个属性，读到的列表不接住。一读就抛，后面的代码不会拿它。
            user.orders
        except InvalidRequestError:
            print("没加载 InvalidRequestError")

    with Session(engine) as session:
        # 另一次会话，另一次查询。options 只作用于这一次 select，不改类上的 lazy="raise"。
        user = session.scalars(
            select(User).options(selectinload(User.orders))
        ).one()
        # 第二条 SQL 用 IN 把这个用户的订单取来。集合已经在手里，点它不再查。
        # [0] 是列表的第一项，下标从 0 开始。对照 list.get(0)。空列表这样取会抛 IndexError。
        # .title 再点这一张订单的普通字段。订单已经加载，不会再发 SQL。
        print("selectin", user.orders[0].title)

    with Session(engine) as session:
        # JOIN 把用户和订单放在同一条 SQL 里。一行用户配一行订单时，结果行会重复。
        # 一个用户两张订单，这条 JOIN 会给出两行，但两行是同一个用户对象。
        # unique() 按主键把重复的用户收成一个。对照 DISTINCT 根实体，不是把订单去重没了。
        # 不写 unique()，joinedload 一对多时 .one() 可能看见多行而失败。
        user = session.scalars(
            select(User).options(joinedload(User.orders))
        ).unique().one()
        print("joined", user.orders[0].title)  # 订单集合已经随 JOIN 填好。再点 [0].title 不再查。

    engine.dispose()  # 关掉连接池。


if __name__ == "__main__":
    main()
