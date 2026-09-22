"""第 15 课示例：logging 基本用法。

对照 Java：
- getLogger(__name__) ≈ LoggerFactory.getLogger(Xxx.class)
- basicConfig ≈ 一份最简 logback.xml
"""

from __future__ import annotations

import logging

# 只在入口配置一次。其它模块不要再 basicConfig。
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_user(user_id: int) -> str:
    """假装查用户。用占位符，不要先 f-string 再传给 logger。"""
    logger.info("查询用户 id=%s", user_id)
    if user_id <= 0:
        logger.warning("非法 id=%s，回退成访客", user_id)
        return "访客"
    return f"user-{user_id}"


def main() -> None:
    logger.debug("这条默认看不到，因为级别是 INFO")
    print("查到:", fetch_user(7))
    print("查到:", fetch_user(-1))
    logger.error("演示一条 error，程序仍继续")


if __name__ == "__main__":
    main()
