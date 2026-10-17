"""第 52 课参考答案。题 1、题 2 都过。题 3 写在下面。

跑出来是：
第一次: ['001']
第二次: []
表: ['schema_versions', 'todos']

自己写了版本表和 001 的建表语句，没有调用示例里的 migrate。
第二次对同一个 engine 再跑，跳过 001，没有因为表已存在而报错。

练习里查表名多包了一层括号，不影响结果。
打印用了全角冒号「第一次：」，题目只要求能看见 001 和空列表，不算错。
这次题 3 用了 #，是注释。上一课那种写在 if 后面的三引号不是。

题 3：
- 生产环境不用 Base.metadata.create_all 代替迁移。
  create_all 只建还不存在的表。已经有数据的表，它不会加列、改列，
  也不会记下这台机器执行过哪一版。两台机器各启动一次，你不知道谁的结构新。
  生产要的是编号过的变更：执行过就跳过，没执行过才跑。
  create_all 适合空库演示。对照 Flyway：sql 有版本号，执行过的记在历史表里。
  工作里这个循环通常交给 Alembic。本课把循环写开，是为了看见它在做什么。
- 版本号和建表语句要放在同一个事务里。
  建表成功、插入版本号失败，下次还会再执行 CREATE TABLE，然后因为表已存在而报错。
  反过来只记了版本号、表没建成，下次会跳过，库里却没有 todos。
  放在同一个 engine.begin() 里：正常结束一起 commit，中途抛错一起 rollback。
"""

from __future__ import annotations

from sqlalchemy import create_engine, text

# 版本号和这一版的 SQL 写在一起。list 的顺序就是执行顺序。
STEPS: list[tuple[str, str]] = [
    (
        "001",
        "CREATE TABLE todos (id INTEGER PRIMARY KEY, title TEXT NOT NULL)",
    ),
]


def applied(connection) -> set[str]:
    """已经执行过的版本号。记账表还不存在时先建它。"""

    connection.execute(
        # 第二次迁移时这张表已经在，不要再报「表已存在」。
        text("CREATE TABLE IF NOT EXISTS schema_versions (version TEXT PRIMARY KEY)")
    )
    rows = connection.execute(text("SELECT version FROM schema_versions")).all()
    return {row[0] for row in rows}  # 集合用来判断「这版在不在」。


def migrate(engine) -> list[str]:
    """返回这一次新执行的版本号。已经记过账的不执行。空列表不是失败。"""

    fresh: list[str] = []
    # 建表和记账在同一个事务里。只做了其中一件，下次会对不上。
    with engine.begin() as connection:
        done = applied(connection)
        for version, sql in STEPS:
            if version in done:
                continue  # 这版已经跑过，不要重复 CREATE。
            connection.execute(text(sql))
            # :version 是占位符。值放在 dict 里，不要用 f-string 拼进 SQL。
            connection.execute(
                text("INSERT INTO schema_versions (version) VALUES (:version)"),
                {"version": version},
            )
            fresh.append(version)  # 记账成功才算这一版是这次新跑的。
    return fresh


def main() -> None:
    engine = create_engine("sqlite:///:memory:")
    print("第一次:", migrate(engine))  # 预期 ['001']。
    print("第二次:", migrate(engine))  # 预期 []。同一句 CREATE 不会再执行。
    with engine.connect() as connection:
        # sqlite_master 是 SQLite 自己的目录。别的数据库没有这张表。
        tables = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")
        ).all()
    print("表:", [row[0] for row in tables])
    engine.dispose()


if __name__ == "__main__":
    main()
