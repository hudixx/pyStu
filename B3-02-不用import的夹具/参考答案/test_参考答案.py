"""选修 B3 第 2 课参考答案。题 1 过了。题 2 写在下面。

只跑练习夹具是 1 passed。整课目录是 2 passed，多出来的 1 个是示例 test_订单.py。
本目录再跑一次也是 1 passed。它和练习夹具各有一份 conftest，互不相干。

conftest.py 里的夹具名叫 phone，返回 400-100-1000。
测试参数名也是 phone，没有 import conftest。断言通过。

函数和 import 之间少了一行空行。本课的 ruff 没把这一条算进检查，不影响测试。
演示文件在顶层函数前面空了两行。

题 2：
- 测试不用 import conftest。pytest 收集这个目录时，会先执行同目录那个固定名字的文件，
  再按参数名把夹具的返回值填进测试。import 拿到的是函数，还要自己调用才有字符串。
  旁边放一个普通 .py，Python 不会因为你写了参数就自动去调它。这是 pytest 的收集规则，不是语法。
- 放在仓库根上，所有课的测试都能看见这份夹具。名字一撞，别的课也会被配上，不好查。
  放在这一课目录里，只覆盖这个目录和它的子目录。对照测试基类只给这个包用。
"""

from __future__ import annotations


def test_phone(phone: str) -> None:
    # 参数名 phone 和夹具函数同名。pytest 调用夹具，把返回的字符串填进来。
    # 不要写 from conftest import phone。那样拿到的是函数。
    assert phone == "400-100-1000"
