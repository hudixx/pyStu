"""第 52 课示例：表结构的变更按编号执行一次，再跑就跳过。

对照 Flyway：sql 文件有版本号，执行过的版本记在一张表里。
工作里这个循环通常交给 Alembic。本课把循环写开，第一次先看见它在做什么。
"""

from __future__ import annotations

from sqlalchemy import create_engine, text

# 版本号 → 这一版要执行的 SQL。顺序按编号，不按字典偶然顺序。
STEPS: list[tuple[str, str]] = [
    (
        "001",
        "CREATE TABLE todos (id INTEGER PRIMARY KEY, title TEXT NOT NULL)",
    ),
]


def applied(connection) -> set[str]:
    """已经执行过的版本号。表还不存在时，先建这张记账表。"""
    connection.execute(
        text("CREATE TABLE IF NOT EXISTS schema_versions (version TEXT PRIMARY KEY)")
    )
    rows = connection.execute(text("SELECT version FROM schema_versions")).all()
    return {row[0] for row in rows}


def migrate(engine) -> list[str]:
    """返回这一次新执行的版本号。已经有的不执行。"""
    fresh: list[str] = []
    # 迁移自己也是一个事务。建表和记账要一起成功。
    with engine.begin() as connection:
        done = applied(connection)
        for version, sql in STEPS:
            if version in done:
                continue
            connection.execute(text(sql))
            connection.execute(
                text("INSERT INTO schema_versions (version) VALUES (:version)"),
                {"version": version},
            )
            fresh.append(version)
    return fresh


def main() -> None:
    engine = create_engine("sqlite:///:memory:")
    print("第一次:", migrate(engine))
    print("第二次:", migrate(engine))
    with engine.connect() as connection:
        tables = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")
        ).all()
    print("表:", [row[0] for row in tables])
    engine.dispose()


if __name__ == "__main__":
    main()
