"""第 09 课示例：Path、读写文本、JSON。

对照 Java：
- pathlib.Path ≈ java.nio.file.Path
- read_text / write_text ≈ Files.readString / writeString
- json ≈ 内置 Jackson，但只认 dict/list 等基本类型
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class User:
    """简单数据类。json 不能直接 dumps 它，要先 asdict。"""

    name: str
    years: int


def main() -> None:
    here = Path(__file__).resolve().parent
    data_dir = here / "demo_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    json_path = data_dir / "users.json"

    print("=== Path 拼接与属性 ===")
    print("脚本目录:", here)
    print("JSON 路径:", json_path)
    print("文件名:", json_path.name)
    print("后缀:", json_path.suffix)

    print("=== 写成 JSON ===")
    users = [User("hudi", 30), User("ada", 1)]
    payload = [asdict(u) for u in users]
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("已写入:", json_path)

    print("=== 读回来 ===")
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    for row in loaded:
        print(f"{row['name']} 学了 {row['years']} 年")

    print("=== glob ===")
    for p in here.glob("*.py"):
        print("本目录 py:", p.name)

    # 演示用完可以留着，练习里你会自己写一份
    print("demo_data/users.json 已生成，可打开看一眼")


if __name__ == "__main__":
    main()
