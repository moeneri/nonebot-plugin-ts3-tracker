from __future__ import annotations

import re

from nonebot import get_driver, get_plugin_config, logger, on_command, on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent
from nonebot.plugin import PluginMetadata

from .config import Config
from .runtime import Ts3TrackerRuntime
from .service import Ts3TrackerService

plugin_config = get_plugin_config(Config).ts3_tracker
service = Ts3TrackerService(plugin_config)
runtime = Ts3TrackerRuntime(plugin_config, service)

__plugin_meta__ = PluginMetadata(
    name="TS3 Tracker",
    description="查询 TeamSpeak 3 服务器在线状态与频道在线成员。",
    usage=(
        "上号\n"
        "/ts\n"
        "/tsinfo\n\n"
        "可选：开启轮询后发送 TS3 进服/退服通知"
    ),
    type="application",
    homepage="https://github.com/moeneri/nonebot_plugin_ts3_tracker",
    config=Config,
    supported_adapters={"nonebot.adapters.onebot.v11"},
)


def _ensure_group_allowed(event: MessageEvent) -> str | None:
    if not isinstance(event, GroupMessageEvent):
        return None
    if plugin_config.is_group_allowed(event.group_id):
        return None
    return "当前群未开启 TS3 查询白名单权限。"


ts3_status = on_command(
    "上号",
    aliases={"ts", "tsinfo"},
    priority=plugin_config.command_priority,
    block=True,
)
ts3_status_regex = on_regex(
    r"^(?:/)?(?:上号|ts|tsinfo)$",
    flags=re.IGNORECASE,
    priority=plugin_config.command_priority,
    block=True,
)


@ts3_status.handle()
async def handle_ts3_status(event: MessageEvent) -> None:
    denied_message = _ensure_group_allowed(event)
    if denied_message is not None:
        await ts3_status.finish(denied_message)

    group_id = getattr(event, "group_id", None)
    logger.info(
        "群号 {} 查询了服务器信息。",
        group_id if group_id is not None else event.get_session_id(),
    )
    message = await service.build_server_message()
    await ts3_status.finish(message)


@ts3_status_regex.handle()
async def handle_ts3_status_regex(event: MessageEvent) -> None:
    denied_message = _ensure_group_allowed(event)
    if denied_message is not None:
        await ts3_status_regex.finish(denied_message)

    group_id = getattr(event, "group_id", None)
    logger.info(
        "群号 {} 查询了服务器信息。",
        group_id if group_id is not None else event.get_session_id(),
    )
    message = await service.build_server_message()
    await ts3_status_regex.finish(message)


driver = get_driver()
driver.on_startup(runtime.startup)
driver.on_shutdown(runtime.shutdown)
