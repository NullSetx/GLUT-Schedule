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
  access_token: "你的钉钉机器人token"
  secret: "你的钉钉机器人密钥"
  message_type: "markdown"

schedule:
  enabled: true
  push_times:
    - "07:30"
    - "21:00"
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

### 1. 创建机器人

1. 打开钉钉群聊
2. 点击群设置 → 智能群助手 → 添加机器人
3. 选择"自定义 (通过 Webhook 接入)"
4. 安全设置选择"加签"
5. 复制 Webhook URL 和密钥

### 2. 配置机器人

从 Webhook URL 中提取 `access_token`：

```
https://oapi.dingtalk.com/robot/send?access_token=你的token
```

将 `access_token` 和 `secret` 填入 `config.yaml`。

## Linux 部署

### 1. 克隆代码

```bash
git clone https://github.com/NullSetx/GLUT-Schedule.git
cd GLUT-Schedule
```

### 2. 安装依赖

```bash
pip3 install -r requirements.txt
```

### 3. 配置

```bash
cp config.example.yaml config.yaml
# 编辑 config.yaml 填入你的配置
```

### 3. 测试运行

```bash
python3 main.py --send
```

### 4. 配置定时任务

```bash
crontab -e
```

添加定时任务 (工作日每天早上 7:30 推送，路径改为你的实际路径)：

```
30 7 * * 1-5 /path/to/GLUT-Schedule/deploy.sh >> /path/to/GLUT-Schedule/logs/cron.log 2>&1
```

| cron 表达式 | 说明 |
|------------|------|
| `30 7 * * 1-5` | 每周一到周五 7:30 |
| `30 7 * * *` | 每天 7:30 |
| `0 9 * * 1` | 每周一 9:00 |

### 5. 查看日志

```bash
tail -f logs/$(date +%Y-%m-%d).log
```

## 依赖

- Python 3.6+
- requests
- pyyaml
- dingtalk-stream
- schedule

---

## 交互式钉钉机器人

在钉钉群里 @机器人 发送消息即可查询课表。

### 前置条件

- 钉钉企业管理员权限
- 企业内部应用

### 配置步骤

#### 1. 创建企业内部应用

1. 登录 https://open-dev.dingtalk.com/
2. 进入 应用开发 → 企业内部应用 → 创建应用
3. 添加机器人能力
4. 记录 AppKey 和 AppSecret

#### 2. 更新配置文件

在 `config.yaml` 中配置机器人信息：

```yaml
edu:
  username: "你的学号"
  password: "你的密码"
  base_url: "http://jw.glut.edu.cn"

dingtalk:
  app_key: "你的AppKey"
  app_secret: "你的AppSecret"
```

#### 3. 启动服务

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

