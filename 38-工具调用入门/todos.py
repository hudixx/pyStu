"""待办工具的真正实现。假模型里没有这份列表。

对照：工单进了 Service 才改数据库。模型文件只负责「填工单」。
后面几课 import 这里，避免每课各写一份然后行为漂移。
第 39 课练习要自己写一份，不要 import 本文件。
"""

from __future__ import annotations

import json  # arguments 是字符串，先 loads 成对象，再交给 pydantic。

# BaseModel：DTO 基类，构造时真校验。ConfigDict：类上的配置，不是 JSON 字段。
# Field：字段约束。ValidationError：校验失败时抛的异常，本文件会把它接住，不往外抛。
from pydantic import BaseModel, ConfigDict, Field, ValidationError

# 进程内的业务状态。对照一张内存里的表，不是对话消息。
# 写在模块顶上，相当于这个模块的 static 字段：谁 import 了 todos，看到的是同一份列表。
# 换一份 messages 不会清空它；要清空得自己调用 reset()。进程退出它才消失。
TODOS: list[str] = []


class AddTodo(BaseModel):
    """add_todo 的入参。对照只有一个字段的 @RequestBody，上面有 @NotBlank 和禁止未知字段。"""

    # model_config 是类变量，pydantic 读它来决定怎么校验。它不会变成 JSON 里的一个字段。
    # extra="forbid"：多一个未知字段就失败。默认是 ignore，那会把脏字段悄悄丢掉。
    # 对照 Jackson 的 FAIL_ON_UNKNOWN_PROPERTIES。
    model_config = ConfigDict(extra="forbid")  # 多一个字段就失败。默认是忽略，那会把脏字段悄悄丢掉。

    title: str = Field(min_length=1, max_length=40)  # "" 过不了。上限避免把整段文章当标题塞进来。


def reset() -> None:
    """测试和示例开头调用。不清的话，上一轮进程里加的标题会留到下一次运行（同一进程内）。"""
    # clear 改的是这个列表对象本身，不是把名字 TODOS 重新绑到一个新列表。
    # 别的模块里写了 from todos import TODOS 拿到的是同一个对象，clear 对它们都可见。
    # 对照 list.clear()。如果写成 TODOS = []，只是本函数里的局部名字，外面的列表不会被换掉。
    TODOS.clear()


def run_tool(name: str, arguments: str) -> str:
    """执行一张工单。永远返回字符串，不把校验失败抛出去。

    返回值会作为 role=tool 的 content 喂回模型。
    抛异常会让整个循环炸掉，模型也看不到「你拒绝了」。
    对照：校验失败转成 400 响应体，而不是让线程把栈打到用户脸上。
    这里先用中文句子，还没有 HTTP。
    """
    # 白名单在解析 JSON 之前。未知名字连参数都不看，更不会按名字去 getattr。
    # not in 后面是元组：两个名字都不是，才算未知。对照 !Set.of(...).contains(name)。
    # 不要写成 getattr(本模块, name)()。模型若给出 drop_database，反射就会去找那个函数。
    if name not in ("list_todos", "add_todo"):
        return f"拒绝: 未知工具 {name}"

    try:
        raw = json.loads(arguments)  # 脏字符串在这里失败。raw 期望是 dict。
    except json.JSONDecodeError:
        # 只抓 JSON 语法错误。别的异常（比如你自己写错）不要在这里吞掉。
        return "拒绝: 参数不是 JSON"

    if name == "list_todos":
        # 列出不接受过滤条件。模型多写了字段，也不能当成「帮我删掉」来用。
        # != {} ：必须正好是空对象。{"title": "x"} 或者 [] 都会被拒绝。对照 !raw.isEmpty()，但这里连类型不对也拒绝。
        if raw != {}:
            return "拒绝: 参数应为空对象"
        if not TODOS:
            # 空列表是假值。没有待办时给模型一句人话，而不是空字符串。空字符串模型更难理解。
            return "待办为空"
        return "、".join(TODOS)  # 给模型看的纯文本。不是再调一次模型。

    # 能走到这里的名字只剩 add_todo。白名单已经排除了别的名字。
    try:
        item = AddTodo.model_validate(raw)  # 构造时真校验。对照 @Valid。失败抛 ValidationError，不是返回 null。
    except ValidationError:
        # 空标题、超长、多了未知字段、title 不是字符串，都进这里。不把 pydantic 的英文错误直接回给模型也行，本课用一句固定的拒绝。
        return "拒绝: title 不合法"
    TODOS.append(item.title)  # 只有校验通过才写。拒绝的那些分支上面已经 return 了。
    return f"已添加 {item.title}"
