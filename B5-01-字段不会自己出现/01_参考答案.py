"""选修 B5 第 1 课参考答案。题 1 过了。题 2 写在下面。

运行 01_练习.py 看到：

默认 下单
带字段 {"event": "下单", "buyer": "hudi", "title": "买豆浆"}

同一句 info，extra 里是 hudi 和买豆浆。默认格式只有消息。自己的 Formatter 把三栏收成 JSON。

字典名叫 patload，后面用的是同一个名字，所以不影响这行 JSON。
format 没写返回类型，title 也没写类型。不影响输出。
注释掉的 StreamHandler(sys.stdout) 没有执行。打开的话，那行会直接打到控制台，和下面两行 print 混在一起。

ruff 报了 3 个没用上的 import：os、subprocess.Handle、sys。输出不受影响，检查过不了。

题 2：
- 两行调用的是同一句 info。第一行的格式是 %(message)s，只取消息「下单」。
  buyer 和 title 挂在 LogRecord 上，格式没去读，就不会出现。
- extra 的键不能叫 message。LogRecord 已经有这个属性。再写一次会抛 KeyError。
  name、args 也是它自己的，同样不能占用。
"""

from __future__ import annotations

import io
import json
import logging


class FieldFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "event": record.getMessage(),
            "buyer": getattr(record, "buyer", "-"),
            "title": getattr(record, "title", "-"),
        }
        return json.dumps(payload, ensure_ascii=False)


def emit(formatter: logging.Formatter, title: str) -> str:
    logger = logging.getLogger("b5.order")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.propagate = False
    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("下单", extra={"buyer": "hudi", "title": title})
    return buffer.getvalue().rstrip("\n")


def main() -> None:
    plain = emit(logging.Formatter("%(message)s"), "买豆浆")
    print("默认", plain)
    rich = emit(FieldFormatter(), "买豆浆")
    print("带字段", rich)


if __name__ == "__main__":
    main()
