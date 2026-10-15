"""第 50 课示例：待办在表里，不在内存列表里。

对照 JPA：Todo 是实体，Session 是一次工作单元，commit 之后才算写入。
数据库用 SQLite 内存库。进程结束，表就没了。本课不留 db 文件。
"""

# 推迟注解求值。后面的 Mapped[int] 在 import 时不会被立刻执行。
from __future__ import annotations

# String：列类型，长度 40。create_engine：造连接池和方言。select：查询语句，还没执行。
from sqlalchemy import String, create_engine, select
# DeclarativeBase：实体的根。Mapped / mapped_column：声明「这个类属性是一列」。
# Session：一次工作单元。对照 EntityManager，不是那张内存里的 list。
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    """所有实体的共同基类。对照 JPA 里带 @Entity 的类要被扫描到的那个根。

    空类体只写文档字符串。继承它的类会被登记到 Base.metadata，create_all 才知道要建哪些表。
    """


class Todo(Base):
    """一张表。类属性是列，不是普通的实例字段。

    写在类体里的 id、title 描述的是表结构。Todo(title="买牛奶") 造出来的对象才是一行。
    对照 @Entity 类里的字段配 @Column，而不是 new 之前先有一行数据。
    """

    __tablename__ = "todos"  # 表名。类名 Todo 不会自动变成表名。对照 @Table(name = "todos")。

    # Mapped[int] 是类型标注，告诉 SQLAlchemy 和 mypy：这一列是整数。对照 @Id int id。
    # primary_key=True：主键。SQLite 的整数主键会自己填，不用你在构造时传入。
    id: Mapped[int] = mapped_column(primary_key=True)  # 主键。SQLite 会自己填整数。
    # String(40) 对照 @Column(length = 40)。超长会在写入时被数据库拒绝，不是 Python 提前截断。
    title: Mapped[str] = mapped_column(String(40))  # 对照 @Column(length = 40)。


def main() -> None:
    # sqlite:///:memory: 是一块只在这个进程里的库。对照 H2 的内存模式，不是 MySQL。
    # 三个斜杠里，最后那个空主机名加 :memory: 表示「不要文件」。进程退出，数据就没了。
    engine = create_engine("sqlite:///:memory:")
    # 按实体建表。教学演示用这一行。生产环境用第 52 课的迁移，不要靠启动时建表。
    # metadata 里登记了所有继承 Base 的表。create_all 只建还没有的表，不会改已经存在的列。
    Base.metadata.create_all(engine)

    # with 结束时关闭 Session，即使中间抛了异常。对照 try-with-resources。
    # 不要做成永远不关的 static 字段。一个 Session 是一次工作单元，用完就关。
    with Session(engine) as session:
        session.add(Todo(title="买牛奶"))  # 先放进会话，这时还没提交。对照 em.persist，事务还没 commit。
        session.commit()  # 提交之后，别的会话才能查到。不 commit 就出了 with，默认会回滚这次新增。
        # select(Todo) 是一句「查出这张表」，此时还没打到库。对照写好 JPQL，还没 getResultList。
        # scalars() 把每一行收成 Todo 对象。不写它，得到的是只有一个元素的元组。
        # .all() 立刻执行，拿回 list。对照 getResultList()。
        rows = session.scalars(select(Todo)).all()
        for row in rows:
            # row.id、row.title 是这一行的字段，不是类上的列描述。对照从实体 getter 里读。
            print(row.id, row.title)

    engine.dispose()  # 关掉连接池。内存库随之丢掉。对照关闭 DataSource。


# 直接 python 本文件才建库、插入、打印。被 import 时不自动连库。
if __name__ == "__main__":
    main()
