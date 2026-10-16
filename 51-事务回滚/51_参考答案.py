"""第 51 课参考答案。题 1、题 2 都过。题 3 写在下面。

跑出来是：
失败: 标题为空
失败后行数: 0
成功后行数: 2

空标题那次，买牛奶和空标题在同一个 begin 里。抛错之后用新 Session 数，是 0。
买面包那次，两行一起提交，是 2。不是失败后留下 1 行、成功后再加 2 行变成 3。

练习里函数名叫 add_par，少了个 i。能跑，但看不出是 pair（一对）。写成 add_pair。

文件最后那对三引号仍不是注释。它写在 if __name__ 后面，main 跑完才执行，
造出一个字符串然后丢掉。上一课已经说过。想留备注，用 #。

题 3：
- 不能先 commit 牛奶，再去插面包。
  那样是两次事务。面包不合法时，牛奶已经提交，回滚只影响第二次。
  库里会留下「买牛奶」一行。题目要的是一起成功，或者一起没有。
  对照一个 @Transactional 方法：中途抛了运行时异常，前面的 persist 不会单独留下。
  两条插入必须放在同一个 begin() 里。里面抛错，begin 先 rollback，再把异常抛出去。
- 同一个还没提交的会话里查到牛奶，不能说明库里已经有了。
  add 之后，这个 Session 里接着查，SQLAlchemy 会先 flush，INSERT 发到当前连接上。
  所以这次会话看得到。那仍是没提交的事务。
  新开一个 Session 看不到。对照：同一个 EntityManager 能看见刚 persist 的对象，
  另一个 EntityManager 要等 commit。
  不 commit 就离开 with，close 会回滚，那一行也不在。
  看见自己刚 add 的对象，只说明它在这次工作单元里。
"""

from __future__ import annotations

from sqlalchemy import String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    """实体的共同基类。继承它的类会登记到 metadata。"""

    pass


class Todo(Base):
    """一行待办。本课关心的是两行在同一个事务里，不是列本身。"""

    __tablename__ = "todos"  # 表名要自己写。类名不会自动变成表名。

    id: Mapped[int] = mapped_column(primary_key=True)  # 主键。SQLite 自己填。
    title: Mapped[str] = mapped_column(String(40))  # 最长 40。


def add_pair(engine, second: str) -> None:
    """两条插入在同一个事务里。second 为空就抛错，第一条也不留。"""

    with Session(engine) as session:
        # 正常走完会 commit。里面抛异常会 rollback，然后异常继续往外抛。
        # 对照一个 @Transactional 方法：正常 return 才提交，抛异常就回滚。
        with session.begin():
            session.add(Todo(title="买牛奶"))  # 放进这个事务。此时别的会话还查不到。
            if second == "":
                # 提交之前失败。不要先 commit 第一条再插第二条，否则牛奶会留下来。
                raise ValueError("标题为空")
            session.add(Todo(title=second))  # 和第二行同一个事务。begin 正常结束才一起提交。


def count_rows(engine) -> int:
    """新开一个会话来数。上一个事务已经结束，这里看到的是提交之后的结果。"""

    with Session(engine) as session:
        # COUNT(*)。scalar() 取出那一个整数。查不到是 None，用 or 0 兜住。
        return session.scalar(select(func.count()).select_from(Todo)) or 0


def main() -> None:
    engine = create_engine("sqlite:///:memory:")  # 进程内的空库。
    Base.metadata.create_all(engine)  # 演示才在这里建表。生产用下一课的迁移。

    try:
        add_pair(engine, "")  # 第二标题是空串，事务中途抛错。
    except ValueError as exc:
        print("失败:", exc)  # 只接这一种。别的异常继续往外走。
    # 用新会话数。应当是 0，第一条买牛奶没有留下。
    print("失败后行数:", count_rows(engine))

    add_pair(engine, "买面包")  # 两行都合法，一起提交。
    print("成功后行数:", count_rows(engine))  # 应当是 2。失败那次没有残留。
    engine.dispose()  # 关掉连接池。


if __name__ == "__main__":
    main()
