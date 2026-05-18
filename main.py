import argparse
import sys
from datetime import date

import requests

from config import load_config, merge_args_with_config
from schedule_api import login, query_schedule, format_schedule, format_schedule_markdown
from dingtalk import DingTalkBot, DingTalkError


def parse_args():
    parser = argparse.ArgumentParser(description="桂林理工大学教务系统课表查询")
    parser.add_argument("-c", "--config", type=str, default="config.yaml", help="配置文件路径 (默认: config.yaml)")
    parser.add_argument("-d", "--data", type=str, help="查询日期，格式: YYYY-M-D 或 YYYY-MM-DD")
    parser.add_argument("-s", "--send", action="store_true", help="发送结果到钉钉")
    parser.add_argument("--text-mode", action="store_true", help="使用文本格式而非 markdown")
    parser.add_argument("-u", "--username", type=str, help="教务系统用户名")
    parser.add_argument("-p", "--password", type=str, help="教务系统密码")
    return parser.parse_args()


def main():
    args = parse_args()

    config = load_config(args.config)
    merged = merge_args_with_config(args, config)

    if merged is None:
        sys.exit(1)

    base_url = merged["edu"]["base_url"]
    username = merged["edu"]["username"]
    password = merged["edu"]["password"]
    date_str = merged["date"] or date.today().strftime("%Y-%m-%d")
    send = merged["send"]

    session = requests.Session()

    print(f"正在登录教务系统...")
    if not login(session, base_url, username, password):
        sys.exit(1)

    print(f"正在查询 {date_str} 的课表...")
    json_data = query_schedule(session, base_url, date_str)

    if json_data is None:
        sys.exit(1)

    schedule_text = format_schedule(json_data)
    print("\n" + "=" * 50)
    print(schedule_text)
    print("=" * 50)

    if send:
        dingtalk_config = merged["dingtalk"]
        access_token = dingtalk_config.get("access_token")
        secret = dingtalk_config.get("secret")

        if not access_token or not secret:
            print("钉钉配置不完整，请检查配置文件中的 dingtalk.access_token 和 dingtalk.secret")
            sys.exit(1)

        bot = DingTalkBot(access_token, secret)

        try:
            if dingtalk_config.get("message_type") == "text":
                result = bot.send_text(schedule_text)
            else:
                title = f"{date_str} 课表"
                markdown_text = format_schedule_markdown(json_data)
                result = bot.send_markdown(title, markdown_text)

            print("\n钉钉消息发送成功")
        except DingTalkError as e:
            print(f"\n钉钉消息发送失败: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
