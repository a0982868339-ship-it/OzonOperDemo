# ──────────────────────────────────────────────
# 后端 Dockerfile（FastAPI + Uvicorn）
# 面试考点：为什么用 slim 镜像？为什么非 root 用户？
# ──────────────────────────────────────────────

# 【基础镜像】
# 用 python:3.11-slim 而不是 python:3.11
# slim = 去掉了编译工具、文档等无用内容
# 镜像体积：slim ~130MB  vs  full ~900MB
# 生产环境原则：镜像越小 = 拉取越快 + 攻击面越小
FROM python:3.11-slim

# 【设置工作目录】
# WORKDIR 会自动创建目录，后续所有操作都在这里进行
# 等价于 mkdir -p /app && cd /app
WORKDIR /app

# 【安装依赖（利用 Docker 缓存层）】
# 为什么先只复制 requirements.txt，而不是直接 COPY . .？
# Docker 每一行指令都是一个"层（Layer）"，只有内容变了才会重新执行
# 代码频繁改动，但依赖很少变动
# → 先 COPY requirements.txt 并 pip install，这一层会被缓存
# → 只要 requirements.txt 不变，下次构建直接复用缓存，速度极快
COPY backend/requirements.txt .

# 安装 Python 依赖
# --no-cache-dir：不保存 pip 缓存到镜像里，减小体积
# --upgrade pip：确保 pip 是最新版，避免安装报错
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 【复制项目代码】
# 此时再复制全部代码，代码改动不会导致依赖重新安装
COPY . .

# 【创建非 root 用户（安全最佳实践）】
# 面试高频考点：为什么容器里不用 root 运行？
# 如果容器被攻破，root 进程可能逃逸到宿主机造成更大危害
# 用非特权用户运行，即使容器被攻击，危害也被限制在容器内
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

# 【声明端口】
# EXPOSE 只是"文档声明"，告诉使用者这个容器监听哪个端口
# 真正的端口映射靠 docker run -p 或 K8s Service 来做
EXPOSE 8001

# 【启动命令】
# uvicorn 是 ASGI 服务器，负责运行 FastAPI 应用
# --host 0.0.0.0：监听所有网卡（容器内必须这么配，否则容器外访问不到）
# --port 8001：对应 EXPOSE 的端口
# backend.main:app：Python 模块路径，找到 FastAPI 的 app 对象
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001"]
