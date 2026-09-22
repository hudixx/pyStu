"""第 09 课参考答案。

读写、ensure_ascii、utf-8、indent、exists/is_file 你都对。
文件名题目是 langs.json，你写成了 lang.json。
dataclass + asdict 是正确思路：json 不认自定义对象，要先变成 dict。
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Lang:
    name: str
    years: int


def main() -> None:
    path = Path(__file__).resolve().parent / "langs.json"
    langs = [Lang("java", 30), Lang("python", 0)]

    with path.open("w", encoding="utf-8") as f:
        json.dump([asdict(lang) for lang in langs], f, ensure_ascii=False, indent=2)

    with path.open("r", encoding="utf-8") as f:
        rows = json.load(f)  # 对文件用 load；loads 是对字符串
    for row in rows:
        print(f"{row['name']} 学了 {row['years']} 年")

    print(path.exists())
    print(path.is_file())
    print(path.name)


if __name__ == "__main__":
    main()
