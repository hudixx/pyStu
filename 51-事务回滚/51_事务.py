"""第 51 课示例：一个事务里的两行，要么都在，要么都不在。

对照 @Transactional。方法中途抛异常，已经 persist 的那一行也会滚回去。
"""

from __future__ import annotations

# func：SQL 函数，比如 COUNT。select 仍是「写好但还没执行」的查询。
from sqlalchemy import String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    # 和上一课一样的根。pass 表示类体为空。对照空的标记基类，不能什么都不写。
    pass


class Todo(Base):
    """和上一课同一张表。本课关心的是两行插在同一个事务里，不是列本身。"""

    __tablename__ = "todos"  # 表名要自己写。类名不会自动变成表名。

    id: Mapped[int] = mapped_column(primary_key=True)  # 主键。SQLite 自己填整数。
    title: Mapped[str] = mapped_column(String(40))  # 最长 40。对照 @Column(length = 40)。


def add_pair(engine, second: str) -> None:
    """两条插入在同一个事务里。second 为空就抛错，第一条也不留。

    engine 没写类型：它是 create_engine 返回的连接池。教学函数先把事务看清楚，不把类型写满。
    """
    with Session(engine) as session:
        # begin() 成功走完会 commit。里面抛异常会 rollback，然后异常继续往外抛。
        # 对照一个 @Transactional 方法：方法正常 return 才提交，抛 RuntimeException 就回滚。
        with session.begin():
            session.add(Todo(title="买牛奶"))  # 放进这个事务。此时别的会话还查不到。
            if second == "":
                # 在提交之前失败。不要先 commit 第一条，再插第二条。那样失败时牛奶会留下来。
                # raise 对照 throw。with 收到异常会先 rollback，再把这个 ValueError 抛给调用方。
                raise ValueError("标题为空")
            session.add(Todo(title=second))  # 第二行和第一行同一个事务。begin() 正常结束才一起提交。


def count_rows(engine) -> int:
    """新开一个会话来数。上一个事务已经结束，这里看到的是提交之后的结果。

    不能用刚才那个已经关闭的 Session。对照新开一个 EntityManager 再查。
    """
    with Session(engine) as session:
        # func.count() 是 SQL 的 COUNT(*)。select_from(Todo) 指定从哪张表数。
        # scalar() 取出第一行第一列那一个值，这里就是一个整数，或查不到时的 None。
        # 对照 query.getSingleResult()，但 None 不会抛 NoResultException，所以用 or 0 兜住。
        return session.scalar(select(func.count()).select_from(Todo)) or 0


def main() -> None:
    engine = create_engine("sqlite:///:memory:")  # 进程内的空库。对照 H2 内存模式。
    Base.metadata.create_all(engine)  # 按 Todo 建表。演示用。生产用第 52 课的迁移。

    try:
        add_pair(engine, "")  # 第二标题是空串，事务中途抛错。
    except ValueError as exc:
        # as exc 把异常对象接住。对照 catch (ValueError e)。只抓这一种，别的异常继续往外走。
        print("失败:", exc)
    # 事务已回滚。用一个新会话数，应当是 0。第一条「买牛奶」没有留下。
    print("失败后行数:", count_rows(engine))

    add_pair(engine, "买面包")  # 两行都合法，一起提交。
    print("成功后行数:", count_rows(engine))  # 应当是 2，不是 1。失败那次没有留下残留的一行。
    engine.dispose()  # 关掉连接池。内存库随之丢掉。


if __name__ == "__main__":
    main()
