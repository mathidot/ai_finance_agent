#!/bin/bash

# AI金融助手启动脚本 (Shell版本)

echo "\033[36m正在启动AI金融助手应用...\033[0m"

# 获取当前脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 启动后端服务
echo "\033[32m正在启动后端服务...\033[0m"
gnome-terminal --title="AI金融助手 - 后端" -- bash -c "cd $SCRIPT_DIR/backend && python main.py; exec bash" 2>/dev/null || \
konsole --new-tab -p tabtitle="AI金融助手 - 后端" -e bash -c "cd $SCRIPT_DIR/backend && python main.py; exec bash" 2>/dev/null || \
terminal -e bash -c "cd $SCRIPT_DIR/backend && python main.py; exec bash" 2>/dev/null || \
xterm -T "AI金融助手 - 后端" -e "cd $SCRIPT_DIR/backend && python main.py; exec bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '$SCRIPT_DIR'/backend && python main.py"' 2>/dev/null || \
echo "\033[31m无法启动新终端窗口，在当前窗口启动后端...\033[0m" && \
(cd $SCRIPT_DIR/backend && python main.py &)

# 等待2秒，确保后端已经启动
sleep 2

# 启动前端服务
echo "\033[32m正在启动前端服务...\033[0m"
gnome-terminal --title="AI金融助手 - 前端" -- bash -c "cd $SCRIPT_DIR/frontend && npm run dev; exec bash" 2>/dev/null || \
konsole --new-tab -p tabtitle="AI金融助手 - 前端" -e bash -c "cd $SCRIPT_DIR/frontend && npm run dev; exec bash" 2>/dev/null || \
terminal -e bash -c "cd $SCRIPT_DIR/frontend && npm run dev; exec bash" 2>/dev/null || \
xterm -T "AI金融助手 - 前端" -e "cd $SCRIPT_DIR/frontend && npm run dev; exec bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '$SCRIPT_DIR'/frontend && npm run dev"' 2>/dev/null || \
echo "\033[31m无法启动新终端窗口，在当前窗口启动前端...\033[0m" && \
(cd $SCRIPT_DIR/frontend && npm run dev &)

echo ""
echo "\033[33m服务已启动！\033[0m"
echo "\033[33m后端服务运行在: http://localhost:3000\033[0m"
echo "\033[33m前端服务运行在: http://localhost:5173\033[0m"
echo ""
echo "\033[36m请在浏览器中访问前端地址以使用应用。\033[0m"
echo "\033[90m按Enter键退出此窗口...\033[0m"
read