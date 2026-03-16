# nonebot-plugin-ts3-tracker

基于 NoneBot2 的 TeamSpeak 3 查询与进服/退服通知插件。

本插件提供以下查询命令：

- `上号`
- `ts`
- `tsinfo`

并补充了适合长期运行的能力：

- TS3 进服通知
- TS3 退服通知
- 5 秒轮询监控
- 在线快照持久化
- 重启后静默同步，避免历史误报
- 频道内玩家在线时长显示
- 群聊 / 私聊主动推送
- 群白名单模式
- 中文日志输出

## 安装

1. 将目录放入 NoneBot2 项目，或作为本地包安装
2. 在机器人项目中加载插件 `nonebot_plugin_ts3_tracker`
3. 配置环境变量

## 基础配置

插件使用以下环境变量：

```env
TS3_TRACKER__SERVER_HOST=127.0.0.1
TS3_TRACKER__SERVER_PORT=9987
TS3_TRACKER__SERVERQUERY_PORT=10011
TS3_TRACKER__SERVERQUERY_USERNAME=your-serverquery-username
TS3_TRACKER__SERVERQUERY_PASSWORD=your-password
TS3_TRACKER__DEBUG=false
```

## 配置

```env
HOST=127.0.0.1
PORT=8080

TS3_TRACKER__SERVER_HOST=127.0.0.1
TS3_TRACKER__SERVER_PORT=9987
TS3_TRACKER__SERVERQUERY_PORT=10011
TS3_TRACKER__SERVERQUERY_USERNAME=your-serverquery-username
TS3_TRACKER__SERVERQUERY_PASSWORD=your-password
TS3_TRACKER__DEBUG=false
TS3_TRACKER__COMMAND_PRIORITY=10
TS3_TRACKER__QUERY_TIMEOUT_SECONDS=10

TS3_TRACKER__NOTIFICATION_ENABLED=true
TS3_TRACKER__NOTIFY_TARGET_GROUPS=123456789
TS3_TRACKER__NOTIFY_TARGET_USERS=
TS3_TRACKER__NOTIFY_BOT_ID=

TS3_TRACKER__GROUP_WHITELIST_ENABLED=false
TS3_TRACKER__GROUP_WHITELIST_GROUPS=

TS3_TRACKER__POLL_INTERVAL_SECONDS=5
TS3_TRACKER__STARTUP_SILENT=true
TS3_TRACKER__DATA_DIR=data/ts3_tracker
```

配置说明：

- `TS3_TRACKER__SERVER_HOST`：TS3 服务器地址
- `TS3_TRACKER__SERVER_PORT`：TS3 语音端口，通常为 `9987`
- `TS3_TRACKER__SERVERQUERY_PORT`：TS3 ServerQuery 端口，通常为 `10011`
- `TS3_TRACKER__SERVERQUERY_USERNAME`：ServerQuery 用户名
- `TS3_TRACKER__SERVERQUERY_PASSWORD`：ServerQuery 密码
- `TS3_TRACKER__DEBUG`：是否输出调试日志
- `TS3_TRACKER__COMMAND_PRIORITY`：命令优先级
- `TS3_TRACKER__QUERY_TIMEOUT_SECONDS`：单次查询超时秒数
- `TS3_TRACKER__NOTIFICATION_ENABLED`：是否启用进服/退服通知
- `TS3_TRACKER__NOTIFY_TARGET_GROUPS`：接收通知的群号，支持逗号、分号、换行分隔
- `TS3_TRACKER__NOTIFY_TARGET_USERS`：接收通知的私聊 QQ，支持逗号、分号、换行分隔
- `TS3_TRACKER__NOTIFY_BOT_ID`：指定发送主动通知的 OneBot v11 Bot ID
- `TS3_TRACKER__GROUP_WHITELIST_ENABLED`：是否开启群白名单模式
- `TS3_TRACKER__GROUP_WHITELIST_GROUPS`：允许使用群命令查询，且允许接收群通知的白名单群号
- `TS3_TRACKER__POLL_INTERVAL_SECONDS`：轮询间隔，默认 `5`
- `TS3_TRACKER__STARTUP_SILENT`：启动时只同步快照，不立刻发送历史在线通知
- `TS3_TRACKER__DATA_DIR`：快照持久化目录

## 群白名单模式

默认情况下：

- 所有群聊都可以使用 `上号`、`ts`、`tsinfo`
- 所有私聊都可以使用查询命令
- 通知只会发给 `TS3_TRACKER__NOTIFY_TARGET_GROUPS` 和 `TS3_TRACKER__NOTIFY_TARGET_USERS`

当开启白名单模式后：

```env
TS3_TRACKER__GROUP_WHITELIST_ENABLED=true
TS3_TRACKER__GROUP_WHITELIST_GROUPS=123456789
```

效果如下：

- 只有白名单群可以使用群聊查询命令
- 私聊仍然可以查询
- 群通知只会发到白名单内，且同时存在于 `TS3_TRACKER__NOTIFY_TARGET_GROUPS` 的群

## 命令

群聊或私聊发送以下任一命令：

```text
上号
ts
tsinfo
```

## 查询返回示例

```text
服务器地址：127.0.0.1:9987
服务器端口：9987
服务器名称：迷你世界高手大会
服务器频道：
APEX: neri(20秒)
原神
守望先锋-归西
穿越火线
永雏塔菲
高能英雄
三国杀
迷你世界
王者荣耀
三角洲行动
```

## 通知示例

进服通知：

```text
让我看看是谁还没上号 👀
🧾 昵称：neri
🟢 上线时间：2026-03-16 00:33:19
📣 neri 进入了 TS 服务器
👥 当前在线人数：3
📜 在线列表：neri, koishi
```

退服通知：

```text
📤 用户下线通知
🧾 昵称：neri
🟢 上线时间：2026-03-16 00:32:51
🔴 下线时间：2026-03-16 01:31:37
⏱️ 在线时长：58分46秒
👥 当前在线人数：2
📜 在线列表：KirA, Cirno
```

## 日志示例

```text
群号 123456789 查询了服务器信息。
neri 进入了服务器。
neri 退出了服务器。
```

## 数据持久化

插件当前不是通过数据库持久化。

它使用本地 JSON 快照文件记录在线状态，默认保存在：

```text
data/ts3_tracker/snapshot.json
```

快照中主要保存：

- 用户唯一标识
- 所在频道
- 首次上线时间
- 已连接时长
- 离开检测所需的对比状态

## 验证

运行单元测试：

```bash
pytest
```

实时验证 TS3 查询：

```bash
python scripts/verify_live.py
```

## NoneBot2 规范确认

已按本地 `nonebot2-master` 文档核对以下要求：

- 使用 `PluginMetadata` 声明插件元信息
- 明确 `config=Config`
- 明确 `supported_adapters={"nonebot.adapters.onebot.v11"}`
- 使用标准 `pyproject.toml` 打包结构
- 根目录包含 `README.md`、`LICENSE`、测试目录与验证脚本
