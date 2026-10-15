# 只给阅读。本课不要求安装 Docker，也不要为了学习去构建这张镜像。
# 对照你在 Java 里写的镜像：进程起来之后，用健康检查判断它还活着。
FROM python:3.13-slim

WORKDIR /app
COPY . /app

# 测试绿了再谈部署。镜像里不要放密钥。
CMD ["python", "-c", "print('ok')"]
