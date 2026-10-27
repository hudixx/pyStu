"""选修 B2 第 1 课：commit 之后属性过期。重新加载过的值会留下，没加载过的再点会脱离。

对照 JPA：提交后持久化上下文里的字段过期。
会话还没关时再点名字，会再查一次。对照还在 EntityManager 里，可以 refresh。
这份值加载进对象之后，with 结束仍能读到它。
从没在提交后再点过的字段，会话关了再点，就是 DetachedInstanceError。
对照没初始化的懒字段，在 EntityManager 关了之后再点。
"""

# 推迟注解求值。后面的 loaded: User 在这一行执行时，User 类还没定义，靠这行才不会立刻去找它。
from __future__ import annotations

# event：往引擎上挂监听，SQL 真正发出去之前会叫你的函数。对照拦截 JDBC 的 Statement。
from sqlalchemy import String, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
# DetachedInstanceError：对象已经不在任何会话里，又去点一个过期字段。对照 EntityManager 关了再点懒字段。
from sqlalchemy.orm.exc import DetachedInstanceError


class Base(DeclarativeBase):
    """实体根。这一课只有一张用户表。继承它的类会登记到 Base.metadata，create_all 才知道建哪张表。"""


class User(Base):
    """一行用户。本课关心的是提交之后这个对象还能不能点。"""

    __tablename__ = "users"  # 表名自己写。类名 User 不会自动变成表名。对照 @Table(name = "users")。

    # Mapped[int] 是「这一列是整数」的标注。mapped_column 才是真正的列。对照 @Id int id。
    id: Mapped[int] = mapped_column(primary_key=True)  # 主键。SQLite 自己填整数，构造时不用传。
    name: Mapped[str] = mapped_column(String(40))  # 最长 40。对照 @Column(length = 40)。


def count_selects(engine, work) -> int:
    """跑 work 期间数 SELECT。插入和建表不算。

    work 是调用方传进来的函数。这里写 work()，才是去调用它。不加括号只是拿到函数本身。
    对照传入一个 Runnable，由这个方法负责 run。
    """

    # {"n": 0} 是字典：键 "n"，值 0。冒号分开键和值。对照 new HashMap 再 put("n", 0)。
    # 不用一个裸的 n = 0，是因为里面的 before 如果写 n += 1，Python 会把 n 当成 before 自己的局部变量，
    # 还没赋值就去读，会抛 UnboundLocalError。改字典里的值不算「给外层名字重新赋值」，所以能改到这份计数。
    seen = {"n": 0}

    def before(conn, cursor, statement, parameters, context, executemany) -> None:
        # 这是嵌套函数，定义在 count_selects 里面。它能看见外层的 seen。对照匿名内部类抓外面的变量。
        # 参数有 6 个，是 SQLAlchemy 规定的监听器签名，少一个就不会被当成这个事件的监听。本课只用 statement。
        # 只数查询。commit 本身通常不发 SELECT。
        # lstrip() 去掉左边的空白。upper() 改成大写。startswith 问是不是以这段开头。三个都是 str 的方法。
        # 对照 trim 只去两端；lstrip 只去左边。upper 对照 toUpperCase。startswith 对照 startsWith。
        if statement.lstrip().upper().startswith("SELECT"):
            seen["n"] += 1  # 用字符串键取出整数再加 1。对照 map.put("n", map.get("n") + 1)。

    # listen 把 before 挂到引擎上。以后每条 SQL 执行前都会调用它。对照注册一个拦截器。
    event.listen(engine, "before_cursor_execute", before)
    try:
        work()  # 调用传进来的那个函数。它里面的查询会被 before 数到。
    finally:
        # 不管 work 成功还是抛了，都卸掉监听。不卸的话，后面别的查询也会被算进这一次。
        # remove 的三个参数要和 listen 时一样：同一个引擎、同一个事件名、同一个函数对象。
        event.remove(engine, "before_cursor_execute", before)
    return seen["n"]  # 取出数好的整数。对照 map.get("n")。


def main() -> None:
    # sqlite:///:memory: 是这块进程里的内存库。对照 H2 内存模式。进程结束，表就没了。
    engine = create_engine("sqlite:///:memory:")
    # 按 User 建表。演示用。生产用迁移，不要靠启动时建表。
    Base.metadata.create_all(engine)
    # 冒号后面只是类型标注，没有赋值。运行时这两行不创造变量。对照「我稍后会把 User 放进这个名字」。
    # 写在 with 外面，是因为 Python 没有块级作用域：with 里面赋值的名字，出来之后还能用。
    # Java 的 try 里面声明的变量，出了花括号就没了。这里正好相反。
    loaded: User
    untouched: User
    # with 结束会关 Session，即使中间抛异常。对照 try-with-resources。关了之后对象就脱离了。
    with Session(engine) as session:
        loaded = User(name="hudi")  # 还没进库的普通对象。id 要等插入之后才有。
        untouched = User(name="li")
        # add_all 一次放入多个。对照循环 em.persist。参数是列表，方括号就是列表。
        session.add_all([loaded, untouched])
        session.commit()  # 默认 expire_on_commit=True。两个对象的名字都过期了。
        # 过期不是把 name 删掉，而是标成「再点就要重新查」。值先从对象上拿掉，避免你读到提交前的旧快照。

        def read_name() -> None:
            # 又一个嵌套函数。定义它不会马上读名字。等下面 count_selects(..., read_name) 里的 work() 才读。
            # 会话还开着。过期不是「没了」，是「再点就再查一次」。
            print("提交后还在会话里", loaded.name)

        # 把函数本身传进去，不要写 read_name()。加了括号会立刻执行，数查询的监听还没挂上。
        selects = count_selects(engine, read_name)
        print("这条读取", selects)  # 预期 1。这一次 SELECT 是过期之后的重新加载。
        # untouched.name 在提交之后没有再点。它一直是过期的。

    # with 已经结束，session 关了。loaded 这个名字还在，因为没有块级作用域。
    # 关掉之前已经重新加载过。脱离之后，这个字段还在对象自己的内存里，所以这里不再查库也能读。
    print("已经加载过", loaded.name)
    try:
        # 点属性就是读。过期的字段加上已经脱离的对象，没有会话可以再查，于是失败。
        # 这一行的值本应传给 print，但一点就抛，print 不会执行。
        print(untouched.name)
    except DetachedInstanceError:
        # 只抓这一种。别的异常继续往外抛。不写 as：不需要异常对象，只要知道是脱离之后点了过期字段。
        print("没加载过 DetachedInstanceError")
    engine.dispose()  # 关掉连接池。内存库随之丢掉。对照关闭 DataSource。


# 直接 python 本文件才跑 main。被 import 时不建库。
if __name__ == "__main__":
    main()
