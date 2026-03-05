# ──────────────────────────────────────────────
# 前端 Dockerfile（Vue3 + Vite → Nginx 静态服务）
# 面试核心考点：多阶段构建（Multi-stage Build）
# ──────────────────────────────────────────────

# ══════════════════════════════════════════════
# Stage 1: 构建阶段（builder）
# 这个阶段只是用来编译，最终镜像里不会包含这些内容
# ══════════════════════════════════════════════
# 用 node:20-alpine 而不是 node:20
# alpine = 基于 Alpine Linux，极小的 Linux 发行版（~5MB）
# node:20 ~950MB → node:20-alpine ~130MB
FROM node:20-alpine AS builder

WORKDIR /app

# 同样利用层缓存！先复制 package.json，再 npm install
# 只要依赖没变，npm install 这一层会直接读缓存，非常快
COPY package.json package-lock.json ./

# npm ci 比 npm install 更适合生产/CI 环境：
# - 严格按照 package-lock.json 安装，保证版本一致性
# - 更快（跳过某些解析步骤），并且失败时会报错而不是悄悄改版本
RUN npm ci

# 再复制所有源码并构建
COPY . .

# vite build 会把 src/ 编译成静态文件放到 dist/ 目录
RUN npm run build

# ══════════════════════════════════════════════
# Stage 2: 运行阶段（最终镜像）
# 面试重点：为什么叫"多阶段"？
# 因为我们用了两个 FROM，每个 FROM 是一个"阶段"
# 最终镜像只包含 Stage 2 的内容
# Stage 1 那些 node_modules（~300MB）完全不会进入最终镜像！
# 最终镜像 ≈ nginx:alpine（~25MB）+ dist文件（几MB）
# ══════════════════════════════════════════════
FROM nginx:alpine

# 把 builder 阶段产出的 dist 目录复制到 Nginx 的静态文件目录
# COPY --from=builder 是多阶段构建的核心语法，跨阶段复制文件
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制自定义 Nginx 配置（处理 Vue Router history 模式 + 反向代理）
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Nginx 默认监听 80 端口
EXPOSE 80

# nginx -g daemon off;
# daemon off = 前台运行，这是容器运行的要求
# 容器只有在前台有进程运行时才保持存活
# 如果 Nginx 以 daemon 模式运行（后台），主进程退出，容器就会立即停止
CMD ["nginx", "-g", "daemon off;"]
