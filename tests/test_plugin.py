from __future__ import annotations

from nonebug import App
import pytest

from nonebot_plugin_ts3_tracker import ts3_status, ts3_status_regex

from utils import FakeMessage, make_fake_event


@pytest.mark.anyio
async def test_command_matcher(monkeypatch: pytest.MonkeyPatch, app: App) -> None:
    async def fake_build_server_message() -> str:
        return "服务器名称：Test"

    monkeypatch.setattr(
        "nonebot_plugin_ts3_tracker.service.build_server_message",
        fake_build_server_message,
    )

    async with app.test_matcher(ts3_status) as ctx:
        bot = ctx.create_bot()
        event = make_fake_event(_message=FakeMessage("/上号"))()
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "服务器名称：Test", True, bot=bot)


@pytest.mark.anyio
async def test_regex_matcher_for_plain_text(
    monkeypatch: pytest.MonkeyPatch, app: App
) -> None:
    async def fake_build_server_message() -> str:
        return "服务器名称：Test"

    monkeypatch.setattr(
        "nonebot_plugin_ts3_tracker.service.build_server_message",
        fake_build_server_message,
    )

    async with app.test_matcher(ts3_status_regex) as ctx:
        bot = ctx.create_bot()
        event = make_fake_event(_message=FakeMessage("上号"))()
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "服务器名称：Test", True, bot=bot)
