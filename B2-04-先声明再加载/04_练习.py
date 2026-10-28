from __future__ import annotations

from sqlalchemy import create_engine, String, event, select, ForeignKey
from sqlalchemy.exc import InvalidRequestError

from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, selectinload, joinedload


class Base(DeclarativeBase):
    """占位"""

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))

    orders: Mapped[list[Order]] = relationship(back_populates="user", lazy="raise")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(20))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="orders")

def seed(engine) -> None:
    with Session(engine) as session:
        hudi = User(name="hudi", orders=[Order(title="买牛奶")])
        session.add(hudi)
        session.commit()
def titles_of(users: list[User]) -> None:
    for user in users:
        for order in user.orders:
            order.title

def main() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    seed(engine)

    with Session(engine) as session:
        user = session.scalars(select(User)).one()
        try:
            print(user.orders[0].title)
        except InvalidRequestError:
            print("没加载 InvalidRequestError")

    with Session(engine) as session:
        user = session.scalars(
            select(User).options(selectinload(User.orders))
        ).one()
    print("selectin", user.orders[0].title)

    with Session(engine) as session:
        user = session.scalars(
            select(User).options(joinedload(User.orders))
        ).unique().one()
    print("joined", user.orders[0].title)
    engine.dispose()


if __name__ == "__main__":
    main()

#  题3不知道，请在参考答案的注释中个给出