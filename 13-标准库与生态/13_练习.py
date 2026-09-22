import argparse
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description= "测试")
    parser.add_argument("--text", required= True)
    parser.add_argument("--times", default= 2, type = int)
    return parser.parse_args()

def main() -> None:
    #第一题
    args = parse_args()
    print(args.text * args.times)
    #第二题
    c = Counter(["java", "python", "java", "go", "python", "java"])
    print(c["java"])
    print(c.most_common(2))
    #第三题
    print(datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M"))
    #第4题
    """
        Python：标准库已经存在的就不用。没有的才需要pip install 
        已经够得：读 JSON 用 json，不必装 Jackson 式的第三方；路径用 pathlib    
        值得装的：HTTP 用 requests / httpx（urllib 太啰嗦）；测试用 pytest（比 unittest 短）
    """



if __name__ == "__main__":
    main()