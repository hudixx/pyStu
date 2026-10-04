# 第 27 课：从请求字段看 temperature 和 token

模型参数不是玄学，是 HTTP JSON 里的字段。计费也不是「调了一次一块钱」，是 **按 token 算**。

运行（仍打第 26 课假模型）：

```bash
PYTHONUTF8=1 python 27-对话参数与token/27_参数.py
```

---

## 1. 几个日常会改的字段

| 字段 | 干什么 | 乱调的后果 |
|---|---|---|
| `messages` | 对话内容 | 把整份文档塞进去 → 又贵又慢，还可能超上下文 |
| `temperature` | 随机程度，常见 0～1 | 越大越跳；要稳定抽取就偏低（0～0.3） |
| `max_tokens` | **输出**上限 | 不是「越大切越好」。截断时 `finish_reason` 常是 `length` |
| `model` | 用哪颗模型 | 各家名字不同，写错就 404 |

假模型会把 `temperature` 回显进回复，并把回复截到 `max_tokens` 个字符（1 字符当 1 token，只为演示）。

```python
resp = await client.chat.completions.create(
    model="mock-chat",
    messages=[{"role": "user", "content": "你好"}],
    temperature=0.0,
    max_tokens=8,
)
```

`temperature=0` 在真模型上仍可能有极小波动；假模型是确定性的，适合写测试。

---

## 2. `usage`：这次花了多少

```python
u = resp.usage
print(u.prompt_tokens, u.completion_tokens, u.total_tokens)
```

| 字段 | 含义 | 谁更大通常更贵 |
|---|---|---|
| `prompt_tokens` | 输入（含 system / 历史 / 检索进来的文档） | 上下文越长越贵 |
| `completion_tokens` | 模型吐出来的字 | 长答案更贵 |
| `total_tokens` | 两者之和 | 账单近似看这个 |

对照：RPC 不计次费；这里 **每次 create 都是钱**。所以：

- 不要把数据库整表拼进 prompt
- 历史对话要截断，不能无限 append
- 能确定的规则写在代码里，别让模型「再想一遍」

后面 RAG 课会再碰到「检索 3 段而不是 30 段」。

---

## 3. system / user 分工

- **system**：你的产品规则。例如「不知道就说不知道」「用 JSON 回答」。
- **user**：不可信输入。用户说「忽略以上指令」时，你仍然把它当 **数据**，不要拼进 system。这是阶段九提示注入的预告。

假模型几乎不看 system，真模型会。练习里还是要写上，养成习惯。

---

## 本课肌肉记忆

1. temperature / max_tokens 是请求字段
2. 看 `usage`，不要只看回复好不好
3. 输入 token 往往比输出更容易被你自己做大
4. 假模型截断按字符，真模型按 tokenizer，数量级意识对即可

下一课：流式。用户不想盯着空白等 8 秒。
