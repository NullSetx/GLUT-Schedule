#!/bin/bash

# 课表自动推送脚本
# 用法: ./deploy.sh [日期]
# 示例: ./deploy.sh 2026-5-20
# 如果不指定日期，默认查询当天

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
PYTHON_BIN="python3"
VENV_DIR="$SCRIPT_DIR/.venv"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志文件 (按日期)
DATE=$(date +%Y-%m-%d)
LOG_FILE="$LOG_DIR/$DATE.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查 Python 环境
check_python() {
    if [ -f "$VENV_DIR/bin/python" ]; then
        PYTHON_BIN="$VENV_DIR/bin/python"
        log "使用虚拟环境: $PYTHON_BIN"
    elif command -v python3 &>/dev/null; then
        PYTHON_BIN="python3"
        log "使用系统 Python: $PYTHON_BIN"
    elif command -v python &>/dev/null; then
        PYTHON_BIN="python"
        log "使用系统 Python: $PYTHON_BIN"
    else
        log "错误: 未找到 Python"
        exit 1
    fi
}

# 安装依赖
install_deps() {
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        if [ -f "$VENV_DIR/bin/pip" ]; then
            "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" -q
        elif command -v pip3 &>/dev/null; then
            pip3 install -r "$SCRIPT_DIR/requirements.txt" -q
        elif command -v pip &>/dev/null; then
            pip install -r "$SCRIPT_DIR/requirements.txt" -q
        fi
        log "依赖已安装"
    fi
}

# 主函数
main() {
    log "开始执行课表推送任务"

    check_python
    install_deps

    # 构建命令
    CMD="$PYTHON_BIN $SCRIPT_DIR/main.py --send"

    # 如果指定了日期，添加日期参数
    if [ -n "$1" ]; then
        CMD="$CMD --data $1"
    fi

    log "执行命令: $CMD"

    # 执行
    eval "$CMD" >> "$LOG_FILE" 2>&1
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        log "任务执行成功"
    else
        log "任务执行失败，退出码: $EXIT_CODE"
    fi

    exit $EXIT_CODE
}

main "$@"
