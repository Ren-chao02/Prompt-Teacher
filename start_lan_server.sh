#!/bin/bash
# ============================================================
# 提示词教学平台 - 局域网部署脚本
# 功能：启动Django服务器，允许局域网内其他设备访问
# 使用方法：./start_lan_server.sh
# 作者：Prompt Teacher Team
# 日期：2024
# ============================================================

set -e  # 遇到错误立即退出

echo "=============================================="
echo "🚀 提示词教学平台 - 局域网服务器启动工具"
echo "=============================================="
echo ""

# 获取本机局域网IP地址
LOCAL_IP=$(hostname -I | awk '{print $1}')

if [ -z "$LOCAL_IP" ]; then
    echo "❌ 错误：无法获取本机IP地址"
    exit 1
fi

# 检查端口是否被占用
PORT=8001
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 $PORT 已被占用，正在尝试释放..."
    fuser -k $PORT/tcp 2>/dev/null || true
    sleep 2
fi

echo "✅ 配置信息："
echo "   📡 本机IP地址：$LOCAL_IP"
echo "   🔌 服务端口：$PORT"
echo "   🌐 访问地址：http://$LOCAL_IP:$PORT/"
echo ""
echo "⏳ 正在启动服务器..."
echo ""

# 进入项目目录
cd "/home/mjl/Prompt Teacher"

# 启动Django开发服务器（监听所有网络接口）
python manage.py runserver 0.0.0.0:$PORT

# 如果上面的命令失败，显示错误信息
if [ $? -ne 0 ]; then
    echo "❌ 服务器启动失败！"
    echo "请检查："
    echo "  1. Django是否正确安装"
    echo "  2. 数据库配置是否正确"
    echo "  3. 端口$PORT是否被占用"
    exit 1
fi
