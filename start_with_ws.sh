#!/bin/bash

echo "=========================================="
echo "🚀 Prompt Teacher - 启动脚本 (含WebSocket)"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/home/mjl/Prompt Teacher"
cd "$PROJECT_DIR" || exit 1

# 停止已存在的进程
echo -e "\n${YELLOW}⏹️  停止已有服务...${NC}"
pkill -f "daphne.*prompt_teaching.asgi" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 2

# 启动Django ASGI服务器 (Daphne - 支持WebSocket)
echo -e "\n${BLUE}[1/2] 启动 Django ASGI Server (Daphne)...${NC}"
daphne -b 0.0.0.0 -p 8002 prompt_teaching.asgi:application > /tmp/django_asgi.log 2>&1 &
DJANGO_PID=$!
sleep 3

if kill -0 $DJANGO_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Django ASGI Server 已启动 (PID: $DJANGO_PID, Port: 8002)${NC}"
    echo -e "   HTTP API: http://localhost:8002/api/v1/"
    echo -e "   WebSocket: ws://localhost:8002/ws/notifications/"
else
    echo -e "${RED}❌ Django ASGI Server 启动失败!${NC}"
    cat /tmp/django_asgi.log | tail -20
    exit 1
fi

# 启动Vite前端开发服务器
echo -e "\n${BLUE}[2/2] 启动 Vite Dev Server...${NC}"
cd "$PROJECT_DIR/admin-panel"
npm run dev > /tmp/vite_dev.log 2>&1 &
VITE_PID=$!
sleep 5

if kill -0 $VITE_PID 2>/dev/null; then
    VITE_PORT=$(grep -oP 'Local:\s+\K\d+' /tmp/vite_dev.log | head -1)
    if [ -z "$VITE_PORT" ]; then
        VITE_PORT="5173"
    fi
    echo -e "${GREEN}✅ Vite Dev Server 已启动 (PID: $VITE_PID, Port: $VITE_PORT)${NC}"
    echo -e "   Frontend: http://localhost:$VITE_PORT/admin/login"
else
    echo -e "${RED}❌ Vite Dev Server 启动失败!${NC}"
    cat /tmp/vite_dev.log | tail -20
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 所有服务已成功启动!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📌 访问地址:${NC}"
echo -e "   管理后台: ${YELLOW}http://localhost:$VITE_PORT/admin/login${NC}"
echo -e "   用户名:   admin"
echo -e "   密码:     admin123"
echo ""
echo -e "${BLUE}📌 API端点:${NC}"
echo -e "   REST API:  http://localhost:8002/api/v1/notifications/"
echo -e "   WebSocket: ws://localhost:8002/ws/notifications/?token=YOUR_JWT_TOKEN"
echo ""
echo -e "${BLUE}📌 日志文件:${NC}"
echo -e "   Django:    /tmp/django_asgi.log"
echo -e "   Vite:      /tmp/vite_dev.log"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"

# 等待用户中断
trap 'echo -e "\n\n${YELLOW}⏹️  正在停止服务...${NC}"; kill $DJANGO_PID $VITE_PID 2>/dev/null; echo -e "${GREEN}✅ 所有服务已停止${NC}"; exit 0' INT TERM

wait
