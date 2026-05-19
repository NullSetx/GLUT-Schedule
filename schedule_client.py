import requests
import warnings


warnings.filterwarnings("ignore")


def login(session, base_url, username, password):
    url_login = f"{base_url}/academic/j_acegi_security_check"

    login_data = {
        "j_username": username,
        "j_password": password,
        "j_captcha": "",
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": f"{base_url}/academic/common/security/login.jsp",
    }

    try:
        resp = session.post(url_login, data=login_data, headers=headers, allow_redirects=False)
        if resp.status_code == 302:
            return True
        else:
            print("登录失败，请检查账号密码")
            return False
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return False


def query_schedule(session, base_url, date):
    url_schedule = f"{base_url}/academic/personal/currentTodayPlan.do"

    params = {"currentDate": date}

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": f"{base_url}/academic/common/security/login.jsp",
    }

    try:
        response = session.post(url_schedule, params=params, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"查询失败，HTTP状态码: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return None
    except Exception as e:
        print(f"发生未知错误: {e}")
        return None


def format_schedule(json_data):
    result = []
    data = json_data.get("data", [])

    if not data:
        return "今天没有课"

    for idx, item in enumerate(data, start=1):
        time_slot = item.get("time", "")
        name = item.get("name", "")
        building = item.get("resBuildingName", "")
        room = item.get("roomName", "")
        start = item.get("startDate", "").split()[-1]
        end = item.get("endDate", "").split()[-1]

        lesson = (
            f"{idx}. {time_slot} | {start} - {end}\n"
            f"   {name}\n"
            f"   {building} {room}"
        )
        result.append(lesson)

    date = data[0]["arrangeDate"].split()[0]
    return f"{date} 课表\n\n" + "\n\n".join(result)


def format_schedule_markdown(json_data):
    data = json_data.get("data", [])

    if not data:
        return "# 今天没有课"

    date = data[0]["arrangeDate"].split()[0]
    lines = [f"# {date} 课表"]

    for idx, item in enumerate(data, start=1):
        time_slot = item.get("time", "")
        name = item.get("name", "")
        building = item.get("resBuildingName", "")
        room = item.get("roomName", "")
        start = item.get("startDate", "").split()[-1]
        end = item.get("endDate", "").split()[-1]

        lines.append(f"{idx}. **{time_slot}** | {start} - {end}")
        lines.append(f"   - {name} @ {building} {room}")

    return "\n".join(lines)
