import time
import hmac
import hashlib
import base64
import urllib.parse
import requests


class DingTalkError(Exception):
    pass


class DingTalkBot:
    def __init__(self, access_token, secret):
        self.access_token = access_token
        self.secret = secret
        self.base_url = "https://oapi.dingtalk.com/robot/send"

    def _sign(self):
        timestamp = str(round(time.time() * 1000))
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            self.secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    def _build_url(self):
        timestamp, sign = self._sign()
        return f"{self.base_url}?access_token={self.access_token}&timestamp={timestamp}&sign={sign}"

    def send_text(self, content, at_all=False, at_mobiles=None):
        url = self._build_url()
        data = {
            "msgtype": "text",
            "text": {"content": content},
            "at": {
                "isAtAll": at_all,
                "atMobiles": at_mobiles or [],
            },
        }

        try:
            resp = requests.post(url, json=data)
            result = resp.json()
            if result.get("errcode") != 0:
                raise DingTalkError(f"钉钉发送失败: {result.get('errmsg')}")
            return result
        except requests.exceptions.RequestException as e:
            raise DingTalkError(f"网络请求错误: {e}")

    def send_markdown(self, title, text, at_all=False):
        url = self._build_url()
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text,
            },
            "at": {
                "isAtAll": at_all,
            },
        }

        try:
            resp = requests.post(url, json=data)
            result = resp.json()
            if result.get("errcode") != 0:
                raise DingTalkError(f"钉钉发送失败: {result.get('errmsg')}")
            return result
        except requests.exceptions.RequestException as e:
            raise DingTalkError(f"网络请求错误: {e}")
