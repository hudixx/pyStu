"""选修 B2 第 3 课：循环里点关系，会变成 1 次加 N 次查询。

对照 Hibernate 的 N+1。先查出两个用户是 1 条 SELECT。
每个用户再点 orders，默认又各查一次，于是变成 3 条。
selectinload 先查出用户，再用一条 IN 查询把订单一起取来，是 2 条。
"""

from __future__ import annotations

# ForeignKey 声明外键列。event 用来数 SELECT。select 是查询对象，这时还没打到库。
from sqlalchemy import ForeignKey, String, create_engine, event, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,  # 类上的关系。点 user.orders 时要不要再查，由它决定。
    selectinload,  # 这次查询额外声明：把 orders 用一条 IN 查询预先取来。
)


class Base(DeclarativeBase):
    """实体根。User 和 Order 都继承它，两张表才会被 create_all 建出来。"""


class User(Base):
    """一个用户，下面有多张订单。关系默认是点到才查。"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))  # 最长 20。本课的名字都很短。
    # 不写 lazy，默认 select：第一次点 user.orders 才发 SQL。对照 @OneToMany(fetch = LAZY)。
    # list[Order] 对照 List<Order>。Order 类写在下面，这里却能写它的名字，是因为文件顶部的
    # from __future__ import annotations 把标注当成字符串，不会在定义 User 时立刻去找 Order。
    # back_populates="user" 和 Order.user 配成一对。两边都写，改一边时另一边的集合也会跟上。
    orders: Mapped[list[Order]] = relationship(back_populates="user")


class Order(Base):
    """一张订单，属于一个用户。"""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(20))
    # ForeignKey("users.id") 是数据库外键，指向 users 表的 id 列。字符串写的是表名，不是类名。
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # 对象上的多对一。back_populates="orders" 指回 User.orders 那个属性名。
    user: Mapped[User] = relationship(back_populates="orders")


def count_selects(engine, work) -> int:
    """只数 work 里的 SELECT。建表和插入不算，因为数之前已经提交过了。

    work 是函数。写 work() 才调用。和上一课同一个办法。
    """

    # 字典用来计数。before 里如果写 n += 1，n 会被当成 before 的局部变量，还没赋值就读，会报错。
    # 改 seen["n"] 是在改字典里的值，不是给外层的名字重新赋值。
    seen = {"n": 0}

    def before(conn, cursor, statement, parameters, context, executemany) -> None:
        # 嵌套函数，能看见外层的 seen。6 个参数是监听器规定的签名，本课只看 statement 这句 SQL。
        # lstrip 去掉左边空白，upper 变大写，startswith 问开头是不是 SELECT。都是字符串方法。
        if statement.lstrip().upper().startswith("SELECT"):
            seen["n"] += 1

    event.listen(engine, "before_cursor_execute", before)  # 每条 SQL 执行前调用 before。
    try:
        work()
    finally:
        # 卸掉监听，避免下一次 count_selects 把上一次的也留着，一条 SQL 被数两次。
        event.remove(engine, "before_cursor_execute", before)
    return seen["n"]


def seed(engine) -> None:
    """两个用户，各一张订单。提交并关掉，避免下一个会话还留着缓存。"""

    with Session(engine) as session:
        # orders=[Order(...)] 构造时就把订单放进关系。方括号是列表，这里只有一个元素。
        # 还没 commit。SQLAlchemy 会先插用户、拿到 id，再把这个 id 填进订单的 user_id。
        hudi = User(name="hudi", orders=[Order(title="买牛奶")])
        li = User(name="li", orders=[Order(title="买面包")])
        session.add_all([hudi, li])  # 两个用户都放进会话。订单因为挂在关系上，会一起被插入。
        session.commit()  # 提交后 with 结束，这个会话关掉。下一节查询是新会话，缓存是空的。


def titles_of(users: list[User]) -> None:
    """点到 orders 才会用到关系。不预加载时，每次点都是一条新的 SELECT。

    这个函数不返回值。它的作用是去点关系，把懒加载触发出来，好让外面数 SELECT。
    """

    for user in users:
        for order in user.orders:
            # 单独写 order.title：读这个属性，然后把读到的值丢掉。Python 允许一行只有表达式。
            # 对照 Java 里不能把 getter 当一条语句却不接住返回值时的那种「我只是想触发加载」。
            # 值没用到没关系。点 user.orders 才是发不发 SQL 的地方；点 title 是订单已经取来之后的普通字段。
            order.title


def main() -> None:
    engine = create_engine("sqlite:///:memory:")  # 一个会话就够，用内存库。对照 H2 内存模式。
    Base.metadata.create_all(engine)  # 按两个实体建两张表。
    seed(engine)  # 数据先提交好。下面数 SELECT 时，插入不会被算进去。

    def lazy() -> None:
        # 嵌套函数。count_selects 会在监听挂上之后调用它。
        with Session(engine) as session:
            # scalars 给出 User 对象，不是一行行的元组。list(...) 是内置函数，把这次查询立刻取完，收成列表。
            # 不包 list 的话，结果还是一个「还没走完的迭代器」。这里先取完用户，再进 titles_of 点订单，数得更清楚。
            users = list(session.scalars(select(User)))
            titles_of(users)  # 两个用户各点一次 orders。默认懒加载，各一条 SELECT。

    def preloaded() -> None:
        with Session(engine) as session:
            # options 只对这一次查询生效。不改关系上的默认 lazy。对照这次查询带一个 EntityGraph。
            # selectinload(User.orders)：先 SELECT 用户，再一条 SELECT ... WHERE user_id IN (...) 把订单取来。
            users = list(
                session.scalars(select(User).options(selectinload(User.orders)))
            )
            titles_of(users)  # 订单已经在集合里。再点 orders 不再发 SQL。

    # 把函数传进去，不要加括号。加了括号会立刻跑，那时监听还没挂上，数出来是 0。
    print("不预加载", count_selects(engine, lazy))  # 1 条用户 + 2 条订单 = 3。
    print("预加载", count_selects(engine, preloaded))  # 1 条用户 + 1 条 IN = 2。
    engine.dispose()  # 关掉连接池。内存库丢掉。


if __name__ == "__main__":
    main()
