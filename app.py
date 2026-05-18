import re
import logging
from datetime import date, timedelta

import requests as http_requests
import dingtalk_stream
from dingtalk_stream import AckMessage
from dingtalk_stream.chatbot import ChatbotHandler
from dingtalk_stream.frames import CallbackMessage

from config import load_config
from schedule_api import login, query_schedule, format_schedule_markdown

config = load_config()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HELP_TEXT = """可用指令：
- 今天课表 / 今天有什么课
- 明天课表 / 明天有什么课
- 后天课表 / 后天有什么课
- 查询2026-5-19课表
- 5-19课表
- 帮助"""


def parse_date_from_text(text):
    """从用户消息中解析日期"""
    text = text.lower().replace(" ", "")

    today = date.today()

    if "今天" in text:
        return today.strftime("%Y-%m-%d")
    if "明天" in text:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    if "后天" in text:
        return (today + timedelta(days=2)).strftime("%Y-%m-%d")
    if "昨天" in text:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    patterns = [
        r"(\d{4})[-.\/](\d{1,2})[-.\/](\d{1,2})",
        r"(\d{1,2})[-.\/](\d{1,2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                return f"{groups[0]}-{groups[1]}-{groups[2]}"
            elif len(groups) == 2:
                year = date.today().year
                return f"{year}-{groups[0]}-{groups[1]}"
    return None


def is_help(text):
    """检查是否是帮助指令"""
    keywords = ["帮助", "help", "指令", "功能", "怎么用", "使用方法"]
    return any(k in text.lower() for k in keywords)


class ScheduleBotHandler(ChatbotHandler):
    def __init__(self):
        super().__init__()

    async def process(self, message: CallbackMessage):
        try:
            incoming_message = dingtalk_stream.ChatbotMessage.from_dict(message.data)
            text_content = incoming_message.text.content.strip() if incoming_message.text else ""
            sender_nick = incoming_message.sender_nick

            logger.info(f"收到消息: {text_content} from {sender_nick}")

            if is_help(text_content):
                self.reply_text(HELP_TEXT, incoming_message)
                return AckMessage.STATUS_OK, "ok"

            query_date = parse_date_from_text(text_content)
            if query_date is None:
                self.reply_text(
                    f"@{sender_nick} 请指定日期，例如：\n- 今天课表\n- 明天有什么课\n- 查询2026-5-19课表\n\n发送【帮助】查看所有指令",
                    incoming_message,
                )
                return AckMessage.STATUS_OK, "ok"

            edu_config = config.get("edu", {})
            base_url = edu_config.get("base_url", "http://jw.glut.edu.cn")
            username = edu_config.get("username", "")
            password = edu_config.get("password", "")

            session = http_requests.Session()
            if not login(session, base_url, username, password):
                self.reply_text("教务系统登录失败，请稍后再试", incoming_message)
                return AckMessage.STATUS_OK, "ok"

            json_data = query_schedule(session, base_url, query_date)
            if json_data is None:
                self.reply_text("课表查询失败，请稍后再试", incoming_message)
                return AckMessage.STATUS_OK, "ok"

            markdown_text = format_schedule_markdown(json_data)
            self.reply_markdown(f"{query_date} 课表", markdown_text, incoming_message)

            return AckMessage.STATUS_OK, "ok"

        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            return AckMessage.STATUS_SYSTEM_EXCEPTION, str(e)


def main():
    dingtalk_config = config.get("dingtalk", {})
    app_key = dingtalk_config.get("app_key")
    app_secret = dingtalk_config.get("app_secret")

    if not app_key or not app_secret:
        logger.error("配置文件缺少 app_key 或 app_secret")
        return

    credential = dingtalk_stream.Credential(app_key, app_secret)
    client = dingtalk_stream.DingTalkStreamClient(credential)

    handler = ScheduleBotHandler()
    client.register_callback_handler("/v1.0/im/bot/messages/get", handler)

    logger.info("机器人已启动，等待消息...")
    logger.info(f"AppKey: {app_key[:8]}...")
    client.start_forever()


if __name__ == "__main__":
    main()
