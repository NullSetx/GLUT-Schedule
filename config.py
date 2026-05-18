import os
import yaml


def load_config(config_path="config.yaml"):
    if not os.path.exists(config_path):
        print(f"配置文件不存在: {config_path}")
        print("请复制 config.example.yaml 为 config.yaml 并填入你的配置")
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"配置文件格式错误: {e}")
        return None

    if not config:
        print("配置文件为空")
        return None

    required_fields = ["edu"]
    for field in required_fields:
        if field not in config:
            print(f"配置文件缺少必需字段: {field}")
            return None

    edu_config = config.get("edu", {})
    if "username" not in edu_config or "password" not in edu_config:
        print("配置文件缺少 edu.username 或 edu.password")
        return None

    return config


def merge_args_with_config(args, config):
    if config is None:
        config = {}

    edu_config = config.get("edu", {})
    dingtalk_config = config.get("dingtalk", {})
    defaults = config.get("defaults", {})

    username = getattr(args, "username", None) or edu_config.get("username")
    password = getattr(args, "password", None) or edu_config.get("password")

    if not username or not password:
        print("缺少用户名或密码，请通过命令行参数或配置文件提供")
        return None

    date = getattr(args, "data", None) or defaults.get("date")

    send = getattr(args, "send", False) or defaults.get("send_to_dingtalk", False)
    text_mode = getattr(args, "text_mode", False)

    merged = {
        "edu": {
            "username": username,
            "password": password,
            "base_url": edu_config.get("base_url", "http://jw.glut.edu.cn"),
        },
        "dingtalk": {
            "access_token": dingtalk_config.get("access_token"),
            "secret": dingtalk_config.get("secret"),
            "message_type": "text" if text_mode else dingtalk_config.get("message_type", "markdown"),
        },
        "date": date,
        "send": send,
    }

    return merged
