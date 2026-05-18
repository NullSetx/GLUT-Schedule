import time
import logging
from datetime import date, timedelta

import schedule
import requests

from config import load_config
from schedule_api import login, query_schedule, format_schedule, format_schedule_markdown
from dingtalk import DingTalkBot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

config = load_config()


def push_schedule(push_type="today"):
    """推送课表到钉钉"""
    try:
        edu_config = config.get("edu", {})
        dingtalk_config = config.get("dingtalk", {})

        base_url = edu_config.get("base_url", "http://jw.glut.edu.cn")
        username = edu_config.get("username", "")
        password = edu_config.get("password", "")

        if push_type == "tomorrow":
            query_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            query_date = date.today().strftime("%Y-%m-%d")

        logger.info(f"开始推送 {query_date} 课表...")

        session = requests.Session()
        if not login(session, base_url, username, password):
            logger.error("教务系统登录失败")
            return

        json_data = query_schedule(session, base_url, query_date)
        if json_data is None:
            logger.error("课表查询失败")
            return

        schedule_text = format_schedule(json_data)
        markdown_text = format_schedule_markdown(json_data)

        logger.info(f"课表查询成功，准备发送到钉钉")

        access_token = dingtalk_config.get("access_token")
        secret = dingtalk_config.get("secret")

        if not access_token or not secret:
            logger.error("钉钉配置不完整")
            return

        bot = DingTalkBot(access_token, secret)
        title = f"{query_date} 课表"
        result = bot.send_markdown(title, markdown_text)

        if result.get("errcode") == 0:
            logger.info("钉钉消息发送成功")
        else:
            logger.error(f"钉钉消息发送失败: {result}")

    except Exception as e:
        logger.error(f"推送失败: {e}")


def setup_schedule():
    """设置定时任务"""
    schedule_config = config.get("schedule", {})

    if not schedule_config.get("enabled", False):
        logger.info("定时推送未启用")
        return

    push_times = schedule_config.get("push_times", [])
    push_type = schedule_config.get("push_type", "today")

    for push_time in push_times:
        schedule.every().day.at(push_time).do(push_schedule, push_type=push_type)
        logger.info(f"已设置定时任务: 每天 {push_time} 推送{push_type}课表")

    if not push_times:
        logger.warning("未设置推送时间")


def main():
    logger.info("定时推送服务启动")

    setup_schedule()

    if not schedule.get_jobs():
        logger.info("没有定时任务，退出")
        return

    logger.info("等待定时任务执行... Ctrl+C 停止")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
