from __future__ import annotations

from sqlalchemy import create_engine, text

STEPS: list[tuple[str, str]] = [
    (
        "001",
        "CREATE TABLE todos (id INTEGER PRIMARY KEY, title TEXT NOT NULL)",
    )
]

def applied(connection) -> set[str]:
    connection.execute(
        text("CREATE TABLE IF NOT EXISTS schema_versions (version TEXT PRIMARY KEY)")
    )
    rows = connection.execute(text("SELECT version FROM schema_versions")).all()
    return {row[0] for row in rows}

def migrate(engine) -> list[str]:
    fresh: list[str] = []
    with engine.begin() as connection:
        done = applied(connection)
        for version, sql in STEPS:
            if version in done:
                continue
            connection.execute(text(sql))
            connection.execute(
                text("INSERT INTO schema_versions (version) VALUES (:version)"),
                {"version": version}
            )
            fresh.append(version)
    return fresh


def main() -> None:
    engine = create_engine("sqlite:///:memory:")
    print("第一次：", migrate(engine))
    print("第二次：", migrate(engine))
    with engine.connect() as connection:
        tables = connection.execute((
            text("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")
        )).all()
    print("表：", [row[0] for row in tables])
    engine.dispose()


if __name__ == "__main__":
    main()

#  题3不知道，请在参考答案的注释中个给出