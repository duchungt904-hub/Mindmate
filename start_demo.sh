#!/bin/bash

# MindMate 快速启动脚本

echo "🚀 MindMate 展示模式启动中..."
echo ""

# 获取本机 IP 地址
echo "📱 访问地址："
echo "-------------------"
echo "本地：http://localhost:5001"
echo ""

# Mac 系统获取 IP
if [[ "$OSTYPE" == "darwin"* ]]; then
    IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)
    if [ ! -z "$IP" ]; then
        echo "局域网：http://$IP:5001"
        echo ""
        echo "📲 手机访问："
        echo "1. 确保手机和电脑连接同一 WiFi"
        echo "2. 在手机浏览器输入：http://$IP:5001"
    fi
fi

echo "-------------------"
echo ""
echo "💡 提示："
echo "- 按 Ctrl+C 停止服务"
echo "- 查看完整展示指南：cat DEMO_GUIDE.md"
echo ""
echo "🎬 启动中..."
echo ""

# 切换到项目目录
cd "$(dirname "$0")"

# 启动应用
python app.py
