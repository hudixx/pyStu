
import logging
import sys

#只需配置第一次
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger(__name__)



def divide(a: int, b: int) -> float:
    if b == 0:
        logger.error("被除数为0")
        raise ZeroDivisionError("除数不能为0")
    else:
        return a / b

def main() -> None:
    print(divide(8, 2))

    try:
        logger.info(divide(1, 0))
    except ZeroDivisionError as e:
        logger.error("已捕获除零，程序继续")
        logger.error(e)


    """
    ok
    """
    """
        题2： 不知道，请简要解答下
    """
if __name__ == '__main__':
    main()

