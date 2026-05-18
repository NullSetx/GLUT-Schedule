#!/bin/bash

# GLUT-Schedule 机器人部署脚本
# 用法: ./deploy-bot.sh

set -e

INSTALL_DIR="/opt/GLUT-Schedule"
SERVICE_NAME="GLUT-Schedule"

echo "=== 开始部署 GLUT-Schedule 机器人 ==="

# 1. 检查是否 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用 root 用户运行: sudo ./deploy-bot.sh"
    exit 1
fi

# 2. 安装依赖
echo "安装系统依赖..."
if command -v apt &> /dev/null; then
    apt update
    apt install -y python3 python3-pip python3-venv
elif command -v yum &> /dev/null; then
    yum install -y python38 python38-pip
elif command -v dnf &> /dev/null; then
    dnf install -y python38 python38-pip
else
    echo "未找到包管理器，请手动安装 Python3.8+"
    exit 1
fi

# 检查 Python 版本
PYTHON_CMD="python3"
if command -v python3.8 &> /dev/null; then
    PYTHON_CMD="python3.8"
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python 版本: $PYTHON_VERSION"

if [ $(echo "$PYTHON_VERSION < 3.8" | bc) -eq 1 ]; then
    echo "错误: 需要 Python 3.8+，当前版本 $PYTHON_VERSION 太老"
    echo "请手动安装 Python 3.8+:"
    echo "  yum install -y python38 python38-pip"
    exit 1
fi

# 3. 克隆或更新代码
if [ -d "$INSTALL_DIR" ]; then
    echo "更新代码..."
    cd "$INSTALL_DIR"
    git pull
else
    echo "克隆代码..."
    git clone https://github.com/NullSetx/GLUT-Schedule.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# 4. 创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    $PYTHON_CMD -m venv .venv
fi

# 5. 安装 Python 依赖
echo "安装 Python 依赖..."
.venv/bin/pip install -r requirements.txt -q

# 6. 检查配置文件
if [ ! -f "config.yaml" ]; then
    echo "请先创建并编辑配置文件: $INSTALL_DIR/config.yaml"
    echo "参考 config.example.yaml"
    exit 1
fi

# 7. 复制服务文件
echo "配置 systemd 服务..."
cp GLUT-Schedule.service /etc/systemd/system/

# 8. 重新加载 systemd
systemctl daemon-reload

# 9. 启动服务
echo "启动服务..."
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# 10. 检查状态
sleep 2
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "=== 部署成功 ==="
    echo "服务状态: 运行中"
    echo "查看日志: journalctl -u $SERVICE_NAME -f"
    echo "重启服务: systemctl restart $SERVICE_NAME"
    echo "停止服务: systemctl stop $SERVICE_NAME"
else
    echo "=== 部署失败 ==="
    echo "查看错误: journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi
