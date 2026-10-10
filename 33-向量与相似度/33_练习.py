import sys
from pathlib import Path
import importlib.util

path = Path(__file__).with_name("33_向量.py")

spec = importlib.util.spec_from_file_location("lesson_vec33", path)
mod = importlib.util.module_from_spec(spec)
sys.modules["lesson_vec33"] = mod
spec.loader.exec_module(mod)

embed = mod.embed
cosine = mod.cosine

def main() -> None:
    print(cosine(embed("退款几天"), embed("购买后 7 天内可以退款")))
    print(cosine(embed("退款几天"), embed("月度会员 99 元")))
    print(cosine(embed("客服电话"), embed("客服电话是 400-100-1000")))
if __name__ == "__main__":
    main()
"""
题2不知道，请在参考答案的注释中个给出
"""