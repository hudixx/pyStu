"""第 50 课参考答案。题 1、题 2 都过。题 3 写在下面。

跑出来是：1 买牛奶。
表名是 todos。插入标题「买牛奶」，commit 之后再查，打印 id 和标题。
插入和查询都在 with Session 里。Session 不是模块级全局变量。

练习里 import 写成了 create_engine,select，逗号后面少了一个空格。
应写成 create_engine, select。逗号后面空一格。
这和等号两边的空格不是同一条规则，不影响这次能不能查到。

文件最后那对三引号不是注释。它写在 if __name__ 后面，main 跑完才会执行到。
执行结果是造出一个字符串，然后丢掉。想留备注，用 #。

题 3：
- add 之后、commit 之前，这一行还不算已经在库里。
  session.add 只把对象放进这次 Session，对照 em.persist。事务还没提交。
  同一个 Session 里接着查，SQLAlchemy 默认会先 flush，把 INSERT 发到当前连接上，
  所以这次查询可能看得到。那仍是未提交的事务，不是已经落库。
  另一个 Session 查不到。对照：同一个 EntityManager 能看见刚 persist 的对象，
  另一个 EntityManager 要等 commit。
  不 commit 就离开 with，close 会回滚，库里没有这一行。
  commit() 之后，别的 Session 才能查到。persist 和 commit 不是同一步。
- 第 38 课的 TODOS 是当前进程里的一个 list。
  进程一停就没了。再开一次 python，又是空的。
  它也没有提交和回滚，写进去的半截撤不回来。别的进程看不见。
  表在 commit 之后，别的 Session 还能查到。
  这课用的是 SQLite 内存库，脚本结束库也会丢，只是为了不在目录里留 db 文件。
  换成 sqlite 文件或 Postgres，进程重启之后那一行还在。
  模型不存待办。写库的是 Session。
"""

from __future__ import annotations

from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    """实体的共同基类。继承它的类会登记到 metadata，create_all 才知道建哪些表。"""


class Todo(Base):
    """一行待办。类属性是列，Todo(title=...) 造出来的对象才是一行。"""

    __tablename__ = "todos"  # 表名要自己写。类名 Todo 不会自动变成表名。

    # 主键。SQLite 的整数主键自己填，构造时不用传 id。
    id: Mapped[int] = mapped_column(primary_key=True)
    # 最长 40。超长由数据库拒绝，不是 Python 提前截断。
    title: Mapped[str] = mapped_column(String(40))


def main() -> None:
    # :memory: 只活在这个进程里。脚本结束，库就没了。
    engine = create_engine("sqlite:///:memory:")
    # 教学演示才在启动时建表。生产用迁移，不靠这一行改已经存在的表。
    Base.metadata.create_all(engine)

    # with 结束时关闭 Session。不要做成永远不关的全局变量。
    with Session(engine) as session:
        # 放进这次会话。此时还没提交，别的会话看不到。
        session.add(Todo(title="买牛奶"))
        # 提交之后才算写进库。不写这一行就离开 with，这次新增会回滚。
        session.commit()
        # select 先只是一句查询。scalars().all() 才执行，拿回 Todo 对象的 list。
        rows = session.scalars(select(Todo)).all()
        for row in rows:
            print(row.id, row.title)

    engine.dispose()  # 关掉连接池。内存库随之丢掉。


if __name__ == "__main__":
    main()
