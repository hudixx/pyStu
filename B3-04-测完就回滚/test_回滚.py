"""选修 B3 第 4 课：测试里 commit 了，收尾仍把这次事务滚回去。

对照 @DataJpaTest：每个测试一个事务，结束回滚，不把「买牛奶」留到下一个测试。
库是 SQLite 内存库，整个文件共用一个引擎。每个测试自己开事务，结束 rollback。
async def 的测试不会自己跑。pytest-asyncio 负责把它放进事件循环。
"""

from __future__ import annotations

import asyncio  # sleep 在这里。事件循环本身不由我们 asyncio.run，交给 pytest-asyncio。

import pytest
# event 用来在连接建立、事务开始时插一段 SQLite 专用的设置。func.count 是 SQL 的 COUNT。
from sqlalchemy import String, create_engine, event, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
# StaticPool：连接池里始终是同一条连接。否则每个连接各有一块 :memory: 库，表和数据对不上。
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    """实体根。create_all 看的是它的 metadata。"""


class Todo(Base):
    """一行待办。测试可以 commit，夹具结束时仍会滚掉。"""

    __tablename__ = "todos"  # 表名自己写。类名不会自动变成表名。

    id: Mapped[int] = mapped_column(primary_key=True)  # 主键。SQLite 自己填整数。
    title: Mapped[str] = mapped_column(String(40))  # 最长 40。对照 @Column(length = 40)。


@pytest.fixture(scope="module")
def engine():
    """这个文件共用一块内存库。表只建一次。

    scope="module" 表示本文件所有测试共用这一次造出来的引擎。对照 @BeforeAll 里建一个 DataSource。
    没有写返回类型。有 yield 的夹具，pytest 拿的是 yield 出去的那个对象，不是函数的返回值。
    """

    # StaticPool 让这块 :memory: 在多次连接之间还是同一块库。
    bound = create_engine(
        "sqlite:///:memory:",  # 三个斜杠加 :memory:：不要文件，数据只在这个进程里。
        # 默认不允许别的线程用同一条 SQLite 连接。pytest 可能换线程，所以关掉。换 PostgreSQL 不要抄。
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(bound, "connect")
    def do_connect(dbapi_connection, connection_record) -> None:
        # listens_for 是装饰器，等价于 event.listen(引擎, "connect", 这个函数)。连接刚建立时调用。
        # 第二个参数 connection_record 是 SQLAlchemy 的连接记录，本课不用。签名仍要留着，否则对不上。
        # SQLite 驱动会自己开事务。不关掉的话，测试里的 commit 会真的落库，外层 rollback 撤不掉。
        # isolation_level = None 是给底层驱动对象赋值，不是 Python 的隔离级别枚举。意思是「不要自己管事务」。
        dbapi_connection.isolation_level = None

    @event.listens_for(bound, "begin")
    def do_begin(conn) -> None:
        # "begin" 事件：SQLAlchemy 正要开始一个事务。上面关掉了驱动自己的事务，所以这里要自己发 BEGIN。
        # 改由 SQLAlchemy 发 BEGIN，外层事务才接得住测试里的保存点。
        # exec_driver_sql 把这句原样交给驱动，不经过 ORM。BEGIN 不是查询，没有结果集。
        conn.exec_driver_sql("BEGIN")

    Base.metadata.create_all(bound)  # 建表。整个文件只做一次，因为这个夹具是 module 作用域。
    yield bound  # 把引擎交给需要 engine 参数的夹具。测试都跑完，才继续下面的 dispose。
    bound.dispose()  # 关掉连接池。对照 @AfterAll 里关闭 DataSource。yield 后面的代码就是清理。


@pytest.fixture
def session(engine):
    """每个测试一个外层事务。测试里的 commit 只提交保存点。

    参数名 engine 和上面的夹具同名。pytest 先准备引擎，再调用本函数。这叫夹具依赖夹具。
    没写 scope，默认 function：每个测试都重新开连接、开事务。对照每个测试方法一个事务。
    """

    connection = engine.connect()  # 从池里借一条连接。用完要还，下面 close。
    transaction = connection.begin()  # 外层事务。测试结束时 rollback 的是这一层，所以插入不会留下来。
    # create_savepoint：测试里 session.commit() 不会把外层事务提交掉。
    # 对照测试方法上的 @Transactional，方法结束回滚，不是真的落库。
    # join_transaction_mode 是 Session 的构造参数。bind=connection 表示用我们借来的这条，不要它自己再借一条。
    bound = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield bound  # 测试函数的参数 session 就是这个对象。测试里的 commit 只释放保存点。
    bound.close()  # 先关会话。对照 em.close()。这时外层事务还没滚。
    transaction.rollback()  # 撤掉这个测试里 commit 过的插入。下一个测试看见的表是空的。
    connection.close()  # 把连接还回池子。对照释放连接，不是关掉整个引擎。


def test_add(session: Session) -> None:
    # session 由上面的夹具注入。这个测试不自己 create_engine。
    session.add(Todo(title="买牛奶"))  # 放进会话。对照 em.persist。这时还不一定发出 INSERT。
    session.commit()  # 提交的是保存点。外层事务还在。别的连接不会把这行当成已经永久提交。
    # scalar 取第一行第一列。COUNT(*) 只有一个数字。对照 getSingleResult。
    found = session.scalar(select(func.count()).select_from(Todo))
    assert found == 1  # 这一次测试里确实插入了。== 比的是整数的值。


def test_clean(session: Session) -> None:
    # 上一个测试结束时外层事务回滚了。这张表又是空的。
    # 这是另一个测试，所以 pytest 又调用了一次 session()，新的外层事务，看不见「买牛奶」。
    found = session.scalar(select(func.count()).select_from(Todo))
    assert found == 0


@pytest.mark.asyncio
async def test_tick() -> None:
    """async def 测试。没有 pytest-asyncio，pytest 不会执行这个协程。

    async def 定义的是协程函数。pytest 默认只调用普通函数，调用这个只会得到一个没人跑的协程。
    mark.asyncio 告诉插件：请把它放进事件循环里 await。对照测试方法返回 CompletionStage，要有人去 join。
    """

    # sleep(0) 马上让出一次控制权，不等待。用来证明这是在事件循环里跑的，不是 time.sleep 堵住线程。
    # await 才能把协程真正往下执行。不写 await，sleep(0) 只是造出一个没人理的协程。
    await asyncio.sleep(0)
    assert True  # 永远为真。这一行的作用是：协程若没被执行，测试根本不会算通过。对照断言「跑到了这里」。
