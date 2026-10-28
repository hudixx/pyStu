from __future__ import annotations

from sqlalchemy import create_engine, String, event, select, ForeignKey

from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, selectinload

class Base(DeclarativeBase):
    """占位"""

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))

    orders: Mapped[list[Order]] = relationship(back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(20))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="orders")

def count_selects(engine, func) -> int:
    seen = {"n": 0}

    def before(conn, cursor, statement, parameters, context, executemany) -> None:
        if statement.lstrip().upper().startswith("SELECT"):
            seen["n"] += 1
    event.listen(engine, "before_cursor_execute", before)
    try:
        func()
    finally:
        event.remove(engine, "before_cursor_execute", before)
    return seen["n"]

def send(engine) -> None:
    with Session(engine) as session:
        hudi = User(name="hudi", orders=[Order(title="买牛奶")])
        li = User(name="li", orders=[Order(title="买面包")])
        session.add_all([hudi, li])
        session.commit()
def titles_of(users: list[User]) -> None:
    for user in users:
        for order in user.orders:
            order.title

def main() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    send(engine)

    def lazy() -> None:
        with Session(engine) as session:
            users = list(session.scalars(select(User)))
            titles_of(users)
    def preloaded() -> None:
        with Session(engine) as session:
            users = list(session.scalars(select(User).options(selectinload(User.orders))))
            titles_of(users)

    print("不预加载", count_selects(engine, lazy))
    print("预加载", count_selects(engine, preloaded))

if __name__ == "__main__":
    main()

#  题3不知道，请在参考答案的注释中个给出