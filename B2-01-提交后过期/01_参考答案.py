"""选修 B2 第 1 课参考答案。题 1、题 2 的现象是对的。题 3 写在下面。

练习跑出来是：
提交后还在会话里 hudi
li
hudi
外层:  hudi
<class 'sqlalchemy.orm.exc.DetachedInstanceError'>

会话还开着时打出了 hudi。关掉之后 hudi 仍能读，li 抛的是 DetachedInstanceError。
这两件事和这课要看的一样。

和题目不完全一样的地方：
- 两个用户分了两次 commit。题目是一起 commit。结果还能看，但 li 入库更晚。
- add 之前点了 li 的名字，所以多打出一行 li。那时他还不是库里的行，只是构造时写上的普通字段。
  第二次 commit 之后，点名字的那行被注释掉了，过期字段没有重新加载。所以关掉再点仍然失败。
  如果在第二次 commit 之后、with 结束之前点了 li，关掉再点就不会抛这个异常。
- 接住的是 Exception，不是 DetachedInstanceError。打印的是类型对象，不是「没加载过 DetachedInstanceError」。
  异常种类是对的。Exception 太宽，别的错误也会被印成一行类型。

题 3：
- 提交之后、会话还没关，还能读到名字。
  commit 把字段标成过期，不是把对象赶出会话。会话还开着，再点名字会再发一条 SELECT，把值装回来。
  对照 EntityManager 还在，可以再加载。
- hudi 关掉之后还能读，li 再点会失败。
  hudi 的名字在关掉之前已经重新加载过，这份值留在对象自己的内存里。再点不再查库。
  li 在提交之后没有再点过，名字一直是过期的。会话关了，没有地方再查，所以是 DetachedInstanceError。
  add 之前点过 li，不算提交后的重新加载。
"""

from __future__ import annotations

from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.orm.exc import DetachedInstanceError


class Base(DeclarativeBase):
    """实体根。"""


class User(Base):
    """一行用户。提交之后，名字会过期。"""

    __tablename__ = "users"

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
        session.add_all([loaded, untouched])
        session.commit()  # 两个名字都过期。对象还在这个会话里。
        # 只点 hudi。这一下会再查一次，把值装回对象。不要在这里点 li。
        print("提交后还在会话里", loaded.name)

    # 关掉之前加载过。脱离之后读的是对象自己的内存。
    print("已经加载过", loaded.name)
    try:
        # li 提交后从没再点过。过期加上脱离，没有会话可以再查。
        print(untouched.name)
    except DetachedInstanceError:
        print("没加载过 DetachedInstanceError")
    engine.dispose()


if __name__ == "__main__":
    main()
