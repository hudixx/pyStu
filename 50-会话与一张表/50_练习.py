from __future__ import annotations
from sqlalchemy import String, create_engine,select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

class Base(DeclarativeBase):
    pass

class Todo(Base):
    # 表名
    __tablename__ = "todos"
    # Mapped 标注类型 primary_key 标注主键
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40))

def main() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(Todo(title="买牛奶"))
        session.commit()
        rows = session.scalars(select(Todo)).all()
        for row in rows:
            print(row.id, row.title)
    engine.dispose()




if __name__ == '__main__':
    main()

"""
 题3不知道，请在参考答案的注释中个给出
"""