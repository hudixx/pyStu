from __future__ import annotations

from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase):
    pass
class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40))

def main() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    loaded: User
    untouched: User
    with Session(engine) as session:
        loaded = User(name="hudi")
        untouched = User(name="li")
        session.add(loaded)
        session.commit()
        print("提交后还在会话里", loaded.name)
        print(untouched.name)
        session.add(untouched)
        session.commit()
        print(loaded.name)
        # print(untouched.name)
    print("外层: ", loaded.name)
    try:
        print("外层: ", untouched.name)
    except Exception as e:
        print(type(e))
    engine.dispose()

if __name__ == "__main__":
    main()

#  题3不知道，请在参考答案的注释中个给出