#!/bin/bash
# cron_setup.sh - 定时任务设置脚本
#
# 使用方法:
#   chmod +x cron_setup.sh
#   ./cron_setup.sh           # 设置定时任务
#   ./cron_setup.sh --remove  # 移除定时任务

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)
MAIN_SCRIPT="$SCRIPT_DIR/main.py"
LOG_FILE="$SCRIPT_DIR/output/cron.log"

# cron 表达式：每周一早上9点执行
CRON_SCHEDULE="0 9 * * 1"
CRON_COMMAND="cd $SCRIPT_DIR && $PYTHON_PATH $MAIN_SCRIPT run --send-email >> $LOG_FILE 2>&1"

show_help() {
    echo "News Collector 定时任务设置"
    echo ""
    echo "使用方法:"
    echo "  ./cron_setup.sh           设置定时任务（每周一9:00执行）"
    echo "  ./cron_setup.sh --remove  移除定时任务"
    echo "  ./cron_setup.sh --status  查看当前状态"
    echo "  ./cron_setup.sh --help    显示帮助"
    echo ""
    echo "默认设置:"
    echo "  执行时间: 每周一早上 9:00"
    echo "  Python: $PYTHON_PATH"
    echo "  日志: $LOG_FILE"
}

setup_cron() {
    # 检查是否已存在
    if crontab -l 2>/dev/null | grep -q "news-collector"; then
        echo "⚠️  定时任务已存在，将更新..."
        remove_cron
    fi
    
    # 添加新任务
    (crontab -l 2>/dev/null; echo "# news-collector: 科技周报定时任务") | crontab -
    (crontab -l 2>/dev/null; echo "$CRON_SCHEDULE $CRON_COMMAND") | crontab -
    
    echo "✅ 定时任务已设置"
    echo ""
    echo "执行时间: 每周一 09:00"
    echo "命令: $CRON_COMMAND"
    echo ""
    echo "日志文件: $LOG_FILE"
    echo ""
    echo "提示: 请确保 .env 文件已正确配置"
}

remove_cron() {
    crontab -l 2>/dev/null | grep -v "news-collector" | crontab -
    echo "✅ 定时任务已移除"
}

show_status() {
    echo "当前 cron 任务:"
    echo ""
    if crontab -l 2>/dev/null | grep -q "news-collector"; then
        crontab -l 2>/dev/null | grep -A1 "news-collector"
        echo ""
        echo "状态: ✅ 已启用"
    else
        echo "状态: ❌ 未设置"
    fi
}

# 主逻辑
case "$1" in
    --help|-h)
        show_help
        ;;
    --remove|-r)
        remove_cron
        ;;
    --status|-s)
        show_status
        ;;
    *)
        setup_cron
        ;;
esac
