# 第 26 课：从 HttpClient 看官方模型 SDK

阶段六开始。这是转岗主课：把模型当成 **会胡说、按 token 计费、可能断流的 HTTP 服务**。

你已经会 httpx。本课换官方 SDK，因为多数国产模型（DeepSeek、通义、月之暗面、智谱……）都提供 **OpenAI 兼容** 的 `/v1/chat/completions`。一套客户端，换 `base_url` 就能打另一家。

**先不学 LangChain。** SDK + pydantic + FastAPI 就是架构。

本课示例 **打本机假模型**，不花钱、不需要真密钥。假服务在 `mock_llm.py`，后面 27–31 都复用。

先装依赖：

```bash
source .venv/Scripts/activate
python -m pip install -e ".[llm]"
```

运行：

```bash
PYTHONUTF8=1 python 26-模型SDK入门/26_sdk.py
```

应看到一行 `回声: 你好, hudi`。

---

## 1. 对照

| Java | 本课 |
|---|---|
| `HttpClient` + DTO | `AsyncOpenAI` + `chat.completions.create` |
| `application.yml` 里的 appKey | 环境变量 `OPENAI_API_KEY`，**不进仓库** |
| 换支付渠道改 baseUrl | `OPENAI_BASE_URL` |
| 同步 OkHttp 堵 Tomcat 线程 | 同步 `OpenAI()` 堵事件循环；用 `AsyncOpenAI`（第 24 课） |

```python
import os
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ.get("OPENAI_BASE_URL"),  # 兼容网关；打官方 OpenAI 可省略
)
resp = await client.chat.completions.create(
    model="mock-chat",
    messages=[
        {"role": "system", "content": "你是助手"},
        {"role": "user", "content": "你好, hudi"},
    ],
)
print(resp.choices[0].message.content)
```

`messages` 就是请求体里的数组，不是魔法。`system` 放规则，`user` 放用户输入，`assistant` 是模型说过的话（多轮时才需要带回去）。

取值：`resp.choices[0].message.content`。空选择、content 为 `None` 在真模型上偶尔发生，后面课再防。

---

## 2. 密钥

| 要 | 不要 |
|---|---|
| `os.environ["OPENAI_API_KEY"]` | 写进 `.py`、写进 git |
| 本机用环境变量或 IDE Run Configuration | 把 `sk-` 贴到聊天记录里交差 |

对照：`application.yml` 里的密码用 `${REDIS_PASSWORD}`，不把生产口令推进仓库。

假模型不校验密钥，但 SDK **拒绝空 key**，所以示例用 `"mock-key"`。打真模型时：

```bash
export OPENAI_API_KEY=sk-你的
export OPENAI_BASE_URL=https://api.deepseek.com
# 各家的 model 名不同，看他们文档，不要抄 gpt-4o 去国内网关
```

同一份代码，只换环境变量。

---

## 3. 假模型怎么用

`start_mock()` 返回 `(server, base_url)`。`base_url` 已经带 `/v1`，直接给 SDK。
`finally: server.shutdown()`，和第 16 / 24 课一样。

后面课的故障注入写在 **最后一条 user 消息** 里：`TRIGGER:429`、`TRIGGER:SLOW`、`TRIGGER:BADJSON`。本课先不用。

---

## 本课肌肉记忆

1. `AsyncOpenAI` + `chat.completions.create`，不是 LangChain
2. 密钥只来自环境变量
3. 兼容网关靠 `base_url`，model 名跟各家走
4. 练习打 mock，真钱以后再说
5. 同步 `OpenAI()` 不要放进 `async def`

下一课：temperature、max_tokens、usage。这些是请求字段，不是调参玄学。
