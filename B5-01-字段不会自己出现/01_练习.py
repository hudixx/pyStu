from __future__ import annotations

import io
import os
import json
import logging
from subprocess import Handle
import sys


class FieldFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        patload = {
            "event": record.getMessage(),
            "buyer": getattr(record, "buyer", "-"),
            "title": getattr(record, "title", "-")
        }
        return json.dumps(patload, ensure_ascii=False)

def emit(formatter: logging.Formatter, title) -> str:
    logger = logging.getLogger("b5.order")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.propagate = False
    # handler = logging.StreamHandler(sys.stdout)
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)

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

#  题2不知道，请在参考答案的注释中个给出