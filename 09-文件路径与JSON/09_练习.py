import json
from dataclasses import asdict, dataclass
from pathlib import Path

@dataclass
class Lang:
    name: str
    years: int

def main() -> None:
    #第一题
    path = Path(__file__).resolve().parent
    lang_json = path / "lang.json"

    #第二题
    # lang_json.write_text(json.dumps([asdict(lang) for lang in langs], ensure_ascii=False, indent=2), encoding="utf-8")
    # texts = json.loads(lang_json.read_text(encoding="utf-8"))
    # for text in texts:
    #     print(f"{text['name']} 学了 {text['years']} 年")
    langs = [Lang("java", 30), Lang("python", 0)]
    with lang_json.open("w", encoding="utf-8") as f:
        json.dump([asdict(lang) for lang in langs], f, ensure_ascii=False, indent=2)
    with lang_json.open("r", encoding="utf-8") as f:
        # reads = json.loads(f.read())
        reads = json.load(f)
    for read in reads:
        print(f"{read['name']} 学了 {read['years']} 年")

    #第三题
    print(lang_json.exists())
    print(lang_json.is_file())
    print(lang_json.name)
    #第四题 不知道

if __name__ == "__main__":
    main()