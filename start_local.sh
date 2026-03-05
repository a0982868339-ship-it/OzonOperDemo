#!/bin/bash

# ==============================================================================
# Ozon AI 工具本地开发启动脚本
# ==============================================================================

echo "=================================================="
echo "🚀 正在启动 Ozon AI 工具本地开发环境..."
echo "=================================================="

# 1. 确保在项目根目录
cd "$(dirname "$0")"

# 2. 检查并启动 Redis
# 我们使用 docker 启动一个本地 Redis 供开发使用
if ! docker ps | grep -q "ozondemo-redis-local"; then
    echo "📦 启动本地 Redis 容器 (端口: 6379)..."
    docker run -d --name ozondemo-redis-local -p 6379:6379 --restart unless-stopped redis:7-alpine > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "⚠️  Redis 容器已存在但已停止，正在重新启动..."
        docker start ozondemo-redis-local > /dev/null 2>&1
    fi
else
    echo "✅ Redis 已在运行 (端口: 6379)"
fi

# 等待 Redis 启动
sleep 2

# 3. 启动后端服务 (FastAPI)
echo "🐍 启动后端 FastAPI 服务..."
# 检查是否安装了依赖 (简易判断)
if [ ! -d "backend/venv" ] && [ ! -f "backend/requirements.txt" ]; then
    echo "⚠️  尚未发现后端虚拟环境，建议优先使用 Makefile 中的 docker-up 进行全容器化启动"
fi

# 在后台启动后端
# 注意：必须在项目根目录启动，否则会导致 ModuleNotFoundError: No module named 'backend' 
if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
fi

# 设置本地开发所需的环境变量
export DATABASE_URL="sqlite:///./data/ozon_ai_tool.db"
export REDIS_URL="redis://localhost:6379"

# 创建 data 目录（如果不存在）
mkdir -p ./data

# 启动 Uvicorn (后台运行)
echo "   ➜ 后端运行在: http://localhost:8001"
# 捕获日志到文件，使用 python3 -m uvicorn 保证兼容性
nohup python3 -m uvicorn backend.main:app --reload --port 8001 > backend_dev.log 2>&1 &
BACKEND_PID=$!

# 4. 启动前端服务 (Vue/Vite)
echo "⚡ 启动前端 Vue 服务..."
cd frontend
# 检查是否存在 node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 正在安装前端依赖..."
    npm install
fi

echo "   ➜ 前端运行在: http://localhost:9006"
echo "=================================================="
echo "🎯 所有服务已启动！"
echo "   - 后端日志: tail -f backend_dev.log"
echo "   - 按 Ctrl+C 停止前端服务器（后端将在后台继续运行）"
echo "   - 如需停止后端，运行: kill $BACKEND_PID"
echo "=================================================="

# 在前台运行前端，这样 Ctrl+C 可以停止
npm run dev

# 当 npm run dev 退出时，询问是否也要停止后端
echo ""
read -p "❓ 前端已停止，是否需要同时停止后端服务? (y/n): " stop_backend
if [ "$stop_backend" = "y" ] || [ "$stop_backend" = "Y" ]; then
    echo "🛑 停止后端服务 (PID: $BACKEND_PID)..."
    kill $BACKEND_PID
    echo "✅ 后端已停止。"
fi
