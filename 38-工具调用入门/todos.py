"""待办工具的真正实现。假模型里没有这份列表。

对照：工单进了 Service 才改数据库。模型文件只负责「填工单」。
后面几课 import 这里，避免每课各写一份然后行为漂移。
第 39 课练习要自己写一份，不要 import 本文件。
"""

from __future__ import annotations

import json  # arguments 是字符串，先 loads 成对象，再交给 pydantic。

from pydantic import BaseModel, ConfigDict, Field, ValidationError

# 进程内的业务状态。对照一张内存里的表，不是对话消息。
# 换一份 messages 不会清空它；要清空得自己调用 reset()。
TODOS: list[str] = []


class AddTodo(BaseModel):
    """add_todo 的入参。对照只有一个字段的 @RequestBody，上面有 @NotBlank 和禁止未知字段。"""

    model_config = ConfigDict(extra="forbid")  # 多一个字段就失败。默认是忽略，那会把脏字段悄悄丢掉。

    title: str = Field(min_length=1, max_length=40)  # "" 过不了。上限避免把整段文章当标题塞进来。


def reset() -> None:
    """测试和示例开头调用。不清的话，上一轮进程里加的标题会留到下一次运行（同一进程内）。"""
    TODOS.clear()


def run_tool(name: str, arguments: str) -> str:
    """执行一张工单。永远返回字符串，不把校验失败抛出去。

    返回值会作为 role=tool 的 content 喂回模型。
    抛异常会让整个循环炸掉，模型也看不到「你拒绝了」。
    对照：校验失败转成 400 响应体，而不是让线程把栈打到用户脸上。
    这里先用中文句子，还没有 HTTP。
    """
    # 白名单在解析 JSON 之前。未知名字连参数都不看，更不会按名字去 getattr。
    if name not in ("list_todos", "add_todo"):
        return f"拒绝: 未知工具 {name}"

    try:
        raw = json.loads(arguments)  # 脏字符串在这里失败。raw 期望是 dict。
    except json.JSONDecodeError:
        return "拒绝: 参数不是 JSON"

    if name == "list_todos":
        # 列出不接受过滤条件。模型多写了字段，也不能当成「帮我删掉」来用。
        if raw != {}:
            return "拒绝: 参数应为空对象"
        if not TODOS:
            return "待办为空"
        return "、".join(TODOS)  # 给模型看的纯文本。不是再调一次模型。

    try:
        item = AddTodo.model_validate(raw)  # 构造时真校验。对照 @Valid。
    except ValidationError:
        return "拒绝: title 不合法"
    TODOS.append(item.title)  # 只有校验通过才写。拒绝的那些分支上面已经 return 了。
    return f"已添加 {item.title}"
