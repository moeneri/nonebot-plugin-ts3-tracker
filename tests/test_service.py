from __future__ import annotations

import pytest

from nonebot_plugin_ts3_tracker.config import Ts3TrackerSettings
from nonebot_plugin_ts3_tracker.models import Ts3OnlineUser, Ts3ServerStatus
from nonebot_plugin_ts3_tracker.query import Ts3QueryError
from nonebot_plugin_ts3_tracker.service import Ts3TrackerService


class DummyClient:
    def __init__(
        self, result: Ts3ServerStatus | None = None, error: Exception | None = None
    ) -> None:
        self.result = result
        self.error = error

    async def fetch_status(self) -> Ts3ServerStatus:
        if self.error:
            raise self.error
        assert self.result is not None
        return self.result


def build_settings(**overrides: object) -> Ts3TrackerSettings:
    base = {
        "server_host": "127.0.0.1",
        "server_port": 9987,
        "serverquery_port": 10011,
        "serverquery_username": "query-user",
        "serverquery_password": "password",
    }
    base.update(overrides)
    return Ts3TrackerSettings(**base)


def test_missing_config_message() -> None:
    service = Ts3TrackerService(build_settings(server_host="", serverquery_username=""))
    assert service.get_missing_required_fields() == ["服务器地址", "ServerQuery 账号"]


def test_group_users_by_channel_and_format() -> None:
    service = Ts3TrackerService(build_settings())
    status = Ts3ServerStatus(
        server_name="东雪莲粉丝俱乐部",
        server_host="127.0.0.1",
        server_port=9987,
        online_count=2,
        channels=[("1", "APEX"), ("5", "原神")],
        users=[
            Ts3OnlineUser(
                nickname="neri",
                channel_id="1",
                channel_name="APEX",
                client_id="1",
                database_id="10",
                unique_id="uid-1",
                client_ip="127.0.0.1",
                connected_duration_seconds=10,
                away=False,
            ),
            Ts3OnlineUser(
                nickname="KirA",
                channel_id="99",
                channel_name="临时频道",
                client_id="2",
                database_id="11",
                unique_id="uid-2",
                client_ip="127.0.0.2",
                connected_duration_seconds=20,
                away=True,
            ),
        ],
    )

    grouped = service.group_users_by_channel(status)
    assert grouped == [("APEX", ["neri(10秒)"]), ("原神", []), ("临时频道", ["KirA(20秒)"])]

    message = service.format_server_status(status)
    assert "服务器地址：127.0.0.1:9987" in message
    assert "服务器名称：东雪莲粉丝俱乐部" in message
    assert "APEX: neri(10秒)" in message
    assert "原神" in message
    assert "临时频道: KirA(20秒)" in message


@pytest.mark.asyncio
async def test_build_server_message_success() -> None:
    result = Ts3ServerStatus(
        server_name="Test",
        server_host="127.0.0.1",
        server_port=9987,
        online_count=1,
        channels=[("1", "APEX")],
        users=[
            Ts3OnlineUser(
                nickname="neri",
                channel_id="1",
                channel_name="APEX",
                client_id="1",
                database_id="10",
                unique_id="uid-1",
                client_ip="127.0.0.1",
                connected_duration_seconds=10,
                away=False,
            )
        ],
    )
    service = Ts3TrackerService(
        build_settings(),
        client_factory=lambda: DummyClient(result=result),  # type: ignore[arg-type]
    )

    message = await service.build_server_message()
    assert "服务器名称：Test" in message
    assert "APEX: neri(10秒)" in message


@pytest.mark.asyncio
async def test_build_server_message_query_error() -> None:
    service = Ts3TrackerService(
        build_settings(),
        client_factory=lambda: DummyClient(error=Ts3QueryError("登录失败")),  # type: ignore[arg-type]
    )

    message = await service.build_server_message()
    assert message == "TS3 查询失败：登录失败"
