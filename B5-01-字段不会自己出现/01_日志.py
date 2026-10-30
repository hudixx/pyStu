"""选修 B5 第 1 课：extra 里的字段不会自己出现在日志行上。

对照 logback 的 pattern。pattern 里没有写 buyer，MDC 里放了也不会打出来。
默认格式只有消息。字段要 Formatter 自己去取。
第 48 课是一次模型调用留下哪些栏。这一课是日志库怎么把栏交出去。不装采集器。
"""

# 推迟注解求值。-> str 这类标注在 import 时不会被执行。
from __future__ import annotations

import io  # StringIO：内存里的文本文件。往它写，不会出现在控制台上。对照 new StringWriter()。
import json  # dumps：把字典收成一行 JSON 文本。对照 writeValueAsString。
import logging  # 标准库日志。对照 slf4j + logback，这里格式和输出都在这个库里。


class FieldFormatter(logging.Formatter):
    """把消息和 extra 收成一行 JSON。默认 Formatter 不会做这件事。

    继承 logging.Formatter，只改 format 这一个方法。对照继承 Layout，自己拼一行。
    解释器不会自动调用它。StreamHandler 在真正输出前会来调 format。
    """

    def format(self, record: logging.LogRecord) -> str:
        """把一条 LogRecord 收成 JSON 字符串。handler 拿到这个返回值再写出去。

        逻辑：
        1. 取出消息正文，放进 event。
        2. 从 record 上取 buyer、title。extra 没给的字段用 "-"，不抛异常。
        3. dumps 成一行文本返回。中文保持原样。
        """

        # getMessage() 是那句消息，这里是「下单」。不是整条日志。
        # 它会把 info 的第一个参数和 args 拼好。本课没有 %s 占位，所以就是「下单」本身。
        # getattr 的第三个值是缺了这个字段时用的。extra 没给 title，不会抛。
        # getattr(对象, 名字, 默认值) 是内置函数。对照反射取字段，没有就用默认值，而不是抛 NoSuchField。
        # record.buyer 在没传 extra 时会 AttributeError。第三个参数 "-" 就是为了避开这个。
        payload = {
            "event": record.getMessage(),
            "buyer": getattr(record, "buyer", "-"),
            "title": getattr(record, "title", "-"),
        }
        # 花括号是字典。键是 JSON 里的字段名，值是刚才取到的字符串。
        # ensure_ascii=False：中文原样写出，不要变成 \\uXXXX。
        return json.dumps(payload, ensure_ascii=False)


def emit(formatter: logging.Formatter, title: str) -> str:
    """用指定的格式打一行，把这行收进字符串。不往控制台打，方便和另一行对照。

    逻辑：
    1. 按固定名字拿到 logger，清掉上次留下的 handler，设成 INFO，并且不往上传。
    2. 接一个写进内存的 handler，套上调用方传来的 formatter。
    3. info 打「下单」，extra 里带 buyer 和 title。
    4. 把内存里的文本取出，去掉末尾换行，返回给 main 去打印。
    """

    # 名字固定。logging 按名字在整个进程里只留一份 logger。
    # getLogger("b5.order") 再调用一次，拿到的是同一个对象。对照 LoggerFactory.getLogger。
    logger = logging.getLogger("b5.order")
    logger.handlers.clear()  # 再跑一次时先拆掉旧的，不然同一行会打两遍。
    # handlers 是这个 logger 上的列表。clear() 把列表清空，列表对象还在。对照 list.clear()。
    logger.setLevel(logging.INFO)  # 低于这个等级的调用直接丢掉。
    # DEBUG 低于 INFO。若写成 logger.debug(...)，这一课的 handler 收不到。对照级别门槛。
    logger.propagate = False  # 不交给根 logger。根上若还有别的 handler，会再打一行。
    # propagate 是普通属性赋值。True 时这条日志还会冒泡到父 logger。对照不要让 root 再打一遍。
    buffer = io.StringIO()  # 内存里的文件。handler 往这里写，不占用真的日志文件。
    # StringIO 有 write、getvalue。对照 StringWriter。它不是磁盘上的文件。
    handler = logging.StreamHandler(buffer)  # 把日志写进上面那个「文件」。对照把 Appender 指到一个 Writer。
    handler.setFormatter(formatter)  # 输出前先用这个格式器把 LogRecord 变成字符串。
    logger.addHandler(handler)  # 挂上。一条日志可以有多个 handler，本课只有这一个。
    # extra 的键会变成 LogRecord 的属性。不要用 message、name、args，那些是它自己的，会抛 KeyError。
    # 不要写成 logger.info(f"下单 {title}")。等级关掉时，f-string 也已经拼完了。
    # f-string 在调用 info 之前就拼好了。级别不够、这行其实不输出时，拼接的代价已经付过。
    # extra= 是关键字参数。字典里的 buyer、title 不会自动出现在格式字符串里，要 Formatter 自己 getattr。
    logger.info("下单", extra={"buyer": "hudi", "title": title})
    return buffer.getvalue().rstrip("\n")  # handler 自己加了换行。比的时候去掉这一下。
    # getvalue() 把内存里写过的全部文本取出，是 str。对照 writer.toString()。
    # rstrip("\\n") 只去掉右边的换行，中间的换行不动。对照 trim 只去两端空白，这里只去指定的换行。


def main() -> None:
    """同一句「下单」、同一份 extra，换两种格式器，看出字段会不会自己出现。

    默认 Formatter 的格式只有消息，打印出来就是「下单」。
    FieldFormatter 会把 buyer 和 title 收进 JSON。
    """

    # %(message)s 只有那句消息。extra 里的 title 在这一行里看不见。
    # "%(message)s" 是 logging 自己的格式，不是 f-string。%(名字)s 表示「从 record 取这个属性，当字符串」。
    # 对照 logback 的 %m。pattern 里没写 buyer，extra 里放了也不会出现。
    plain = emit(logging.Formatter("%(message)s"), "买牛奶")
    print("默认", plain)
    rich = emit(FieldFormatter(), "买牛奶")  # 不传格式串。format 方法自己决定输出长什么样。
    print("带字段", rich)


if __name__ == "__main__":
    main()

# 这个脚本想说明的事：
# extra 只是把字段放进 LogRecord。默认那一行格式里没有这些名字，它们就不会打出来。
# 要字段，就自己写 Formatter，用 getattr 去取；没有这个字段时给一个默认值，避免抛 AttributeError。
# 打日志用固定消息加 extra，不要先用 f-string 把内容拼进消息。级别关掉时，f-string 也已经算过了。
