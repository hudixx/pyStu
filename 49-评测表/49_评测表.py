"""第 49 课示例：用 pandas 读第 44 课那种评测表，算出两版的通过率。

对照：SELECT 版本, AVG(通过) FROM eval GROUP BY 版本。
不是转数据分析。只会读、过滤、按组取平均。
"""

from __future__ import annotations

from pathlib import Path  # 用本文件的位置找同目录的 CSV，不依赖你在哪个目录里执行 python。

import pandas as pd  # 第三方包，要在 venv 里安装。pd 是习惯别名。对照一个带列名的表，而不是自己解析 CSV。

# 和本文件同目录。不依赖你从哪个目录启动。
# __file__ 是本 .py。resolve() 变绝对路径。parent 是文件夹。/ 拼接文件名。
_CSV = Path(__file__).resolve().parent / "评测结果.csv"


def main() -> None:
    # read_csv 得到一张表，类型是 DataFrame。对照从 CSV 读进 List，但带列名，可以按列算。
    # 文件不存在会抛 FileNotFoundError。编码默认按内容猜，这份表是 utf-8 的中文列名。
    frame = pd.read_csv(_CSV)
    print("行数", len(frame))  # len 是行数，不是列数。对照 resultSet 的行数，不是列数。

    # groupby：按「版本」分组。["通过"] 先取出这一列，mean 是组里的平均。1 全过，0 全不过，平均就是通过率。
    # as_index=False：版本仍是普通列，不要变成索引。打印时更好读。对照 GROUP BY 之后版本还是 SELECT 里的一列。
    rate = frame.groupby("版本", as_index=False)["通过"].mean()
    # to_string 把表画成对齐的文本。index=False 不印最左边那列行号。对照自己遍历打印，这里交给库。
    print(rate.to_string(index=False))

    # frame["版本"] 是整列。== "简短版" 得到一列 True/False，不是一个布尔值。对照对每一行做判断。
    # 两个条件用 &，每一边要加括号。& 的优先级比 == 高，不加括号会先做别的运算，报错或筛错。
    # 不能写成 and。and 要求整个对象是一个真假值，一列真假值没有「单一的真假」，会抛异常。
    # 对照 SQL 的 WHERE 版本 = '简短版' AND 通过 = 0。
    failed = frame[(frame["版本"] == "简短版") & (frame["通过"] == 0)]
    print("简短版失败", len(failed), "条")  # len 仍是筛完之后的行数。


# 直接运行本文件才读 CSV。被 import 时不自动打印。
if __name__ == "__main__":
    main()
