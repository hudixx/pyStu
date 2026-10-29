"""选修 B5 第 1 课：extra 里的字段不会自己出现在日志行上。

对照 logback 的 pattern。pattern 里没有写 buyer，MDC 里放了也不会打出来。
默认格式只有消息。字段要 Formatter 自己去取。
第 48 课是一次模型调用留下哪些栏。这一课是日志库怎么把栏交出去。不装采集器。
"""

from __future__ import annotations

import io
import json
import logging


class FieldFormatter(logging.Formatter):
    """把消息和 extra 收成一行 JSON。默认 Formatter 不会做这件事。"""

    def format(self, record: logging.LogRecord) -> str:
        # getMessage() 是那句消息，这里是「下单」。不是整条日志。
        # getattr 的第三个值是缺了这个字段时用的。extra 没给 title，不会抛。
        payload = {
            "event": record.getMessage(),
            "buyer": getattr(record, "buyer", "-"),
            "title": getattr(record, "title", "-"),
        }
        # ensure_ascii=False：中文原样写出，不要变成 \\uXXXX。
        return json.dumps(payload, ensure_ascii=False)


def emit(formatter: logging.Formatter, title: str) -> str:
    """用指定的格式打一行，把这行收进字符串。不往控制台打，方便和另一行对照。"""

    # 名字固定。logging 按名字在整个进程里只留一份 logger。
    logger = logging.getLogger("b5.order")
    logger.handlers.clear()  # 再跑一次时先拆掉旧的，不然同一行会打两遍。
    logger.setLevel(logging.INFO)  # 低于这个等级的调用直接丢掉。
    logger.propagate = False  # 不交给根 logger。根上若还有别的 handler，会再打一行。
    buffer = io.StringIO()  # 内存里的文件。handler 往这里写，不占用真的日志文件。
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # extra 的键会变成 LogRecord 的属性。不要用 message、name、args，那些是它自己的，会抛 KeyError。
    # 不要写成 logger.info(f"下单 {title}")。等级关掉时，f-string 也已经拼完了。
    logger.info("下单", extra={"buyer": "hudi", "title": title})
    return buffer.getvalue().rstrip("\n")  # handler 自己加了换行。比的时候去掉这一下。


def main() -> None:
    # %(message)s 只有那句消息。extra 里的 title 在这一行里看不见。
    plain = emit(logging.Formatter("%(message)s"), "买牛奶")
    print("默认", plain)
    rich = emit(FieldFormatter(), "买牛奶")
    print("带字段", rich)


if __name__ == "__main__":
    main()
