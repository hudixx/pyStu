# 第 53 课：从请求作用域看 Depends

库地址来自环境变量。每个请求拿到自己的 `Session`，请求结束就提交并关闭。不要做一个全局 Session 给所有请求共用。

运行：

```bash
PYTHONUTF8=1 python 53-配置与Depends/53_依赖.py
```

应看到创建 `200`，列表里有 `买牛奶`。不启动 uvicorn。`TestClient` 和第 20 课一样，不占端口。

---

## 1. 请求就是事务的边界

```text
请求进来 → get_session 打开 Session
路由函数 add
没抛错 → commit
无论成败 → close
```

对照 Spring 里一个 `@Transactional` 的请求边界，不是 Open Session In View 那种把会话拖过整个渲染。

`flush` 只是让这一次会话里能读到新 id。提交仍在 `Depends` 的后半段。路由里提前 `commit`，后面再失败就收不回来了。

内存库要加 `StaticPool`。否则每个连接各有一块空库，第二次请求会说没有这张表。文件库没有这个问题。本课用内存库，是为了跑完不留文件。

---

## 本课肌肉记忆

1. `DATABASE_URL` 放环境变量，代码里只留内存库这个默认值
2. 一个请求一个 `Session`
3. `commit` 放在请求结束，不放在路由中间
