# ──────────────────────────────────────────────
# Makefile：把所有常用命令封装成简短别名
# 面试考点：为什么要 Makefile？
# 答：团队协作中，新人不需要记住一大串命令
#     make docker-up 比 docker-compose up --build 更直观
# ──────────────────────────────────────────────

.PHONY: help docker-build docker-up docker-down k8s-apply k8s-delete k8s-status

# 默认 target：打印帮助信息
help:
	@echo ""
	@echo "========== ozondemo 部署命令 =========="
	@echo ""
	@echo "【Docker 阶段（本地开发）】"
	@echo "  make docker-build   - 构建所有镜像"
	@echo "  make docker-up      - 启动所有服务（后台）"
	@echo "  make docker-logs    - 查看日志"
	@echo "  make docker-down    - 停止并删除容器"
	@echo ""
	@echo "【K8s 阶段（集群部署）】"
	@echo "  make k8s-apply      - 部署到 K8s 集群"
	@echo "  make k8s-status     - 查看 Pod 状态"
	@echo "  make k8s-delete     - 删除所有 K8s 资源"
	@echo ""

# ══════════════════════════════════════════════
# Docker 命令
# ══════════════════════════════════════════════

# 构建镜像（不启动）
docker-build:
	@echo "🔨 构建后端镜像..."
	docker build -f backend/Dockerfile -t ozondemo-backend:latest .
	@echo "🔨 构建前端镜像..."
	docker build -f frontend/Dockerfile -t ozondemo-frontend:latest ./frontend

# 启动所有服务（--build 会自动重新构建有变化的镜像）
docker-up:
	@echo "🚀 启动所有服务..."
	mkdir -p ./data
	docker-compose up --build -d
	@echo "✅ 服务已启动！"
	@echo "   前端: http://localhost:3000"
	@echo "   后端: http://localhost:8001"
	@echo "   健康: http://localhost:8001/health"

# 查看实时日志
docker-logs:
	docker-compose logs -f

# 停止并删除所有容器（但保留数据卷）
docker-down:
	docker-compose down

# 完全清理（包括数据卷）
docker-clean:
	docker-compose down -v

# ══════════════════════════════════════════════
# Kubernetes 命令
# ══════════════════════════════════════════════

# 把镜像加载到 minikube（本地测试用）
minikube-load:
	@echo "📦 加载镜像到 minikube..."
	minikube image load ozondemo-backend:latest
	minikube image load ozondemo-frontend:latest

# 部署所有 K8s 资源（按依赖顺序）
k8s-apply:
	@echo "🚀 部署到 K8s..."
	# 先部署基础配置
	kubectl apply -f k8s/configmap.yaml
	kubectl apply -f k8s/secret.yaml
	kubectl apply -f k8s/pvc.yaml
	# 再部署服务（Redis 先，后端依赖 Redis）
	kubectl apply -f k8s/redis-deployment.yaml
	kubectl apply -f k8s/backend-deployment.yaml
	kubectl apply -f k8s/frontend-deployment.yaml
	# 最后部署路由
	kubectl apply -f k8s/ingress.yaml
	@echo "✅ 部署完成！用 make k8s-status 查看状态"

# 或者一次性 apply 整个目录（K8s 会自动处理顺序）
k8s-apply-all:
	kubectl apply -f k8s/

# 查看所有资源状态
k8s-status:
	@echo "=== Pod 状态 ==="
	kubectl get pods
	@echo ""
	@echo "=== Service 状态 ==="
	kubectl get services
	@echo ""
	@echo "=== Ingress 状态 ==="
	kubectl get ingress

# 查看 Pod 日志
k8s-logs-backend:
	kubectl logs -l app=backend -f

k8s-logs-frontend:
	kubectl logs -l app=frontend -f

# 删除所有 K8s 资源
k8s-delete:
	kubectl delete -f k8s/

# 进入后端 Pod 调试
k8s-shell-backend:
	kubectl exec -it $$(kubectl get pod -l app=backend -o jsonpath='{.items[0].metadata.name}') -- /bin/sh
