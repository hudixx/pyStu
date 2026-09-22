import functools
from collections.abc import Iterator


def evens(limit: int) -> Iterator[int]:
    temp = 0
    while temp < limit:
        yield temp
        temp += 2

def twice(func):
    """调用原函数两次，返回第二次的结果。"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        result = func(*args, **kwargs)
        return result
    return wrapper

@twice
def ping() -> str:
    print("pong")
    return "ok"


def main() -> None:
    #第一题
    print(list(evens(7)))
    for x in evens(7):
        print(x)
    gen = evens(7)
    print("next 第一次", next(gen))
    print("next 第二次", next(gen))
    # 第二题
    print(ping())
    # 第三题
    print(sum(x for x in range(1, 11) if x % 2 == 0))
    # 第四题
    """
    return [0,2,4,6] 马上占一整张表；yield 对标 Java 的 Iterator / Stream：你要下一个，我才给下一个。
    装饰器 vs @Transactional
        相同：都不改业务方法内部，在外面加一层行为；调用方仍写 ping() / service.save()。
        不同：Python 的 @twice 就是函数，f = twice(f)，没有代理框架、没有字节码增强。Spring 注解要容器、代理、切点；Python 装饰器 import
        进来就能用。能力也更窄：默认只管「包住这一个函数」，不是整条对象图的事务边界。
         
    """


if __name__ == '__main__':
    main()