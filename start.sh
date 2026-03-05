#!/bin/bash

# ==============================================================================
# Ozon AI 工具 快速启动脚本 (基于 Docker)
# 等同于运行: docker-compose up --build -d
# ==============================================================================

echo "=================================================="
echo "🐳 正在通过 Docker 启动 Ozon AI 工具..."
echo "=================================================="

# 1. 确保在项目根目录
cd "$(dirname "$0")"

# 2. 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ 错误: Docker 未运行，请先启动 Docker Desktop！"
    exit 1
fi

# 3. 创建数据目录
mkdir -p ./data

# 4. 停止旧的容器并重新构建启动
echo "🔄 正在构建并启动服务..."
docker-compose down
docker-compose up --build -d

if [ $? -eq 0 ]; then
    echo "=================================================="
    echo "✅ 所有服务已成功启动！"
    echo "   🌐 前端页面: http://localhost:3000"
    echo "   🔌 后端 API: http://localhost:8001"
    echo "   ⚕️  后端监控: http://localhost:8001/health"
    echo "=================================================="
    echo "💡 常用命令提示:"
    echo "   - 查看所有日志: docker-compose logs -f"
    echo "   - 查看后端日志: docker-compose logs -f backend"
    echo "   - 停止所有服务: docker-compose down"
else
    echo "❌ 启动失败，请查看上面的错误信息。"
fi
