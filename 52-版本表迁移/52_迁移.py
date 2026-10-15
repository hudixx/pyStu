"""第 52 课示例：表结构的变更按编号执行一次，再跑就跳过。

对照 Flyway：sql 文件有版本号，执行过的版本记在一张表里。
工作里这个循环通常交给 Alembic。本课把循环写开，第一次先看见它在做什么。
"""

from __future__ import annotations

# create_engine 仍是连接池。text() 把字符串包成 SQL，不要用 f-string 把值拼进语句。
# 对照 PreparedStatement。用户数据走参数，不走字符串拼接。
from sqlalchemy import create_engine, text

# 版本号 → 这一版要执行的 SQL。顺序按编号，不按字典偶然顺序。
# 用 list 而不是 dict：遍历顺序就是写在这里的顺序。对照 Flyway 按版本号排序，不靠文件名碰巧。
# 全大写是约定，不是语言强制的常量。
STEPS: list[tuple[str, str]] = [
    (
        "001",
        "CREATE TABLE todos (id INTEGER PRIMARY KEY, title TEXT NOT NULL)",
    ),
]


def applied(connection) -> set[str]:
    """已经执行过的版本号。表还不存在时，先建这张记账表。

    -> set[str] 对照 Set<String>。集合用来做「这个版本在不在」，不关心顺序。
    """
    connection.execute(
        # IF NOT EXISTS：第二次迁移时记账表已经在，不要再报「表已存在」。
        text("CREATE TABLE IF NOT EXISTS schema_versions (version TEXT PRIMARY KEY)")
    )
    # .all() 立刻拿回全部行。每一行是元组，版本号在下标 0。对照 ResultSet 的第一列。
    rows = connection.execute(text("SELECT version FROM schema_versions")).all()
    # 集合推导：花括号，不是列表的方括号。对照把第一列收进一个 HashSet。
    return {row[0] for row in rows}


def migrate(engine) -> list[str]:
    """返回这一次新执行的版本号。已经有的不执行。

    返回空列表表示「这次没有新变更」，不是失败。对照 Flyway 的 migrate 报告跑了哪些版本。
    """
    fresh: list[str] = []  # 这一次真正执行了的版本。已经记过账的不放进来。
    # engine.begin()：借一条连接，并开一个事务。块正常结束就 commit，抛异常就 rollback。
    # 建表和记账要一起成功。只建了表、没插入版本号，下次会再执行同一句 CREATE，然后失败。
    with engine.begin() as connection:
        done = applied(connection)  # 在同一个事务里读记账表。刚建的空表就是空集合。
        for version, sql in STEPS:
            if version in done:
                continue  # 这版已经跑过。跳到下一版，不要重复 CREATE。
            connection.execute(text(sql))  # 本课的 SQL 没有外部参数，整句来自 STEPS，不是用户输入。
            connection.execute(
                # :version 是占位符。值放在第二个参数的 dict 里。对照 PreparedStatement 的 ?。
                # 不要写成 f"... VALUES ('{version}')"。版本号一旦来自外部，拼接就是 SQL 注入。
                text("INSERT INTO schema_versions (version) VALUES (:version)"),
                {"version": version},
            )
            fresh.append(version)  # 记账成功才算这一版是「这次新跑的」。
    return fresh


def main() -> None:
    engine = create_engine("sqlite:///:memory:")  # 空库。第一次 migrate 要建两张表：todos 和 schema_versions。
    print("第一次:", migrate(engine))  # 预期 ['001']。
    print("第二次:", migrate(engine))  # 预期 []。同一句 CREATE 不会再执行。
    # connect() 只借连接，不包住「我要改结构」的事务。这里是只读查询。用完归还连接。
    with engine.connect() as connection:
        tables = connection.execute(
            # sqlite_master 是 SQLite 自己的目录，列出库里的对象。别的数据库没有这张表。
            text("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")
        ).all()
    # 列表推导：每行元组的第 0 列是表名。对照 stream.map(row -> row.getString(1)).toList()，下标从 0 起。
    print("表:", [row[0] for row in tables])
    engine.dispose()  # 关掉连接池。内存库丢掉。


if __name__ == "__main__":
    main()
