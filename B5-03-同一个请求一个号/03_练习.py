from __future__ import annotations

import contextvars

trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="-")

def downstream() -> None:
    print("下游", trace_id.get())

def handle(request_id: str) -> None:
    token = trace_id.set(request_id)

    try:
        print("入口", trace_id.get())
        downstream()
    finally:
        trace_id.reset(token)

def main() -> None:
    handle("R-9")
    print("结束后", trace_id.get())

if __name__ == "__main__":
    main()

#  题2不知道，请在参考答案的注释中个给出