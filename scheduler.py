import json
import time
import logging
from datetime import date, timedelta

import schedule
import requests

from config import load_config
from schedule_client import login, query_schedule, format_schedule_markdown

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

config = load_config()


def get_access_token(app_key, app_secret):
    """通过 DingTalk Open API 获取 access_token"""
    url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
    data = {
        "appKey": app_key,
        "appSecret": app_secret,
    }
    try:
        resp = requests.post(url, json=data)
        result = resp.json()
        if "accessToken" in result:
            return result["accessToken"]
        else:
            logger.error(f"获取 access_token 失败: {result}")
            return None
    except Exception as e:
        logger.error(f"获取 access_token 异常: {e}")
        return None


def send_message_to_group(access_token, robot_code, chat_id, title, markdown_text):
    """通过 DingTalk Open API 发送 markdown 消息到群聊"""
    url = "https://api.dingtalk.com/v1.0/robot/groupMessages/send"
    headers = {
        "Content-Type": "application/json",
        "x-acs-dingtalk-access-token": access_token,
    }
    data = {
        "robotCode": robot_code,
        "openConversationId": chat_id,
        "msgKey": "sampleMarkdown",
        "msgParam": json.dumps({"title": title, "text": markdown_text}),
    }
    try:
        resp = requests.post(url, json=data, headers=headers)
        result = resp.json()
        return result
    except Exception as e:
        logger.error(f"发送消息异常: {e}")
        return {"processQueryKey": None, "error": str(e)}


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

        markdown_text = format_schedule_markdown(json_data)

        logger.info("课表查询成功，准备发送到钉钉")

        app_key = dingtalk_config.get("app_key")
        app_secret = dingtalk_config.get("app_secret")
        chat_id = dingtalk_config.get("chat_id")

        if not app_key or not app_secret:
            logger.error("钉钉配置不完整，缺少 app_key 或 app_secret")
            return

        if not chat_id:
            logger.error("钉钉配置不完整，缺少 chat_id (openConversationId)")
            logger.info("请在 config.yaml 中添加 chat_id 配置项")
            return

        access_token = get_access_token(app_key, app_secret)
        if not access_token:
            return

        title = f"{query_date} 课表"
        result = send_message_to_group(access_token, app_key, chat_id, title, markdown_text)

        if result.get("processQueryKey"):
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
