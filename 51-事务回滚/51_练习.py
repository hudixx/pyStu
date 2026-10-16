
from __future__ import annotations

from sqlalchemy import String, create_engine, func, select

from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

class Base(DeclarativeBase):
    pass

class Todo(Base):
    __tablename__ = "todos"


    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40))

def add_par(engine, second: str) -> None:
    with Session(engine) as session:
        with session.begin():
            session.add(Todo(title="买牛奶"))
            if second == "":
                raise ValueError("标题为空")
            session.add(Todo(title=second))

def count_rows(engine):
    with Session(engine) as session:
        return session.scalar(select(func.count()).select_from(Todo)) or 0

def main() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    try:
        add_par(engine, '')
    except ValueError as e:
        print("失败:", e)
    print("失败后行数:", count_rows(engine))

    add_par(engine, '买面包')
    print("成功后行数:", count_rows(engine))
    engine.dispose() # 关掉连接池

if __name__ == '__main__':
    main()

#题3不知道，请在参考答案的注释中个给出









