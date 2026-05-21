# GLUT课表查询工具

自动查询教务系统课表，并支持发送到钉钉群。

## 功能

- 查询教务系统课表
- 支持命令行参数和配置文件
- 钉钉机器人消息推送
- 定时自动推送
- 交互式机器人 (需企业内部应用)

## 文件说明

| 文件 | 说明 |
|------|------|
| `main.py` | 主入口脚本 |
| `app.py` | 交互式机器人 (Stream 模式) |
| `scheduler.py` | 定时推送服务 |
| `config.yaml` | 配置文件 (需自行创建) |
| `config.example.yaml` | 配置文件模板 |
| `deploy.sh` | Linux 部署脚本 |
| `schedule_api.py` | 课表查询逻辑 |
| `dingtalk.py` | 钉钉机器人模块 |
| `config.py` | 配置加载模块 |

## 快速开始

### 1. 安装依赖

```bash
pip3 install -r requirements.txt
```

### 2. 配置

复制配置文件模板并填入你的信息：

```bash
cp config.example.yaml config.yaml
```

编辑 `config.yaml`：

```yaml
edu:
  username: "你的学号"
  password: "你的密码"
  base_url: "http://jw.glut.edu.cn"

dingtalk:
  app_key: "你的AppKey"
  app_secret: "你的AppSecret"
  # 群聊 ID，定时推送和手动发送时需要
  # 获取方式: 在钉钉群聊中 @机器人 发送任意消息，查看服务器日志中的 openConversationId
  chat_id: "你的群聊ID"
  message_type: "markdown"

schedule:
  enabled: true
  push_times:
    - time: "07:30"
      type: "today"
    - time: "23:00"
      type: "tomorrow"
  push_type: "today"
```

### 3. 运行

```bash
# 查询今天课表
python3 main.py

# 查询指定日期
python3 main.py --data 2026-5-20

# 查询并发送到钉钉
python3 main.py --send

# 启动定时推送服务
python3 scheduler.py
```

## 命令行参数

| 参数 | 简写 | 说明 |
|------|------|------|
| `--config` | `-c` | 配置文件路径 (默认: config.yaml) |
| `--data` | `-d` | 查询日期 (格式: YYYY-M-D) |
| `--send` | `-s` | 发送到钉钉 |
| `--text-mode` | | 使用文本格式而非 markdown |
| `--username` | `-u` | 覆盖配置文件中的用户名 |
| `--password` | `-p` | 覆盖配置文件中的密码 |

## 钉钉机器人配置

### 1. 创建企业内部应用

1. 登录 https://open-dev.dingtalk.com/
2. 进入 应用开发 → 企业内部应用 → 创建应用
3. 添加机器人能力
4. 记录 AppKey 和 AppSecret

### 2. 配置机器人

将 `app_key` 和 `app_secret` 填入 `config.yaml`。

### 3. 获取群聊 ID (chat_id)

1. 将机器人添加到钉钉群聊
2. 在群聊中 @机器人 发送任意消息
3. 查看服务器日志中的 `openConversationId`:
   ```bash
   journalctl -u GLUT-Schedule -f
   ```
4. 将获取到的 ID 填入 `config.yaml` 的 `chat_id` 字段

## Linux 部署

### 环境要求

- Python 3.9+
- 推荐使用 [uv](https://github.com/astral-sh/uv) 管理 Python 环境和依赖

### 部署步骤

#### 1. 安装 uv (可选，推荐)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. 克隆代码

```bash
git clone https://github.com/NullSetx/GLUT-Schedule.git
cd GLUT-Schedule
```

#### 3. 创建虚拟环境并安装依赖

```bash
# 使用 uv
uv venv --python 3.11
uv pip install -r requirements.txt

# 或使用 venv + pip
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

#### 4. 配置

```bash
cp config.example.yaml config.yaml
# 编辑 config.yaml 填入你的配置
```

#### 5. 测试运行

```bash
.venv/bin/python app.py
```

#### 6. 配置 systemd 服务 (开机自启动)

```bash
# 复制服务文件
sudo cp GLUT-Schedule.service GLUT-Schedule-Scheduler.service /etc/systemd/system/

# 重新加载 systemd
sudo systemctl daemon-reload

# 启动交互式机器人服务
sudo systemctl enable GLUT-Schedule
sudo systemctl start GLUT-Schedule

# 启动定时推送服务
sudo systemctl enable GLUT-Schedule-Scheduler
sudo systemctl start GLUT-Schedule-Scheduler
```

### 服务管理

```bash
# 查看状态
sudo systemctl status GLUT-Schedule
sudo systemctl status GLUT-Schedule-Scheduler

# 重启服务
sudo systemctl restart GLUT-Schedule
sudo systemctl restart GLUT-Schedule-Scheduler

# 停止服务
sudo systemctl stop GLUT-Schedule
sudo systemctl stop GLUT-Schedule-Scheduler

# 查看日志
sudo journalctl -u GLUT-Schedule -f
sudo journalctl -u GLUT-Schedule-Scheduler -f
```

## 依赖

- Python 3.9+
- requests
- pyyaml
- dingtalk-stream
- schedule

---

## 交互式钉钉机器人

在钉钉群里 @机器人 发送消息即可查询课表。

### 前置条件

- 钉钉企业管理员权限
- 企业内部应用 (见上方配置步骤)

### 启动服务

```bash
python3 app.py
```

### 使用方式

1. 将机器人添加到钉钉群聊
2. 在群聊中 @机器人 发送消息:

```
@课表机器人 查询2026-5-19的课表
```

支持的日期格式:
- `查询2026-5-19的课表`
- `课表5-19`
- `5-19`
- `明天，后天，今天有什么课`

