from __future__ import annotations

from datetime import datetime

import pytest

from nonebot_plugin_ts3_tracker.config import Ts3TrackerSettings
from nonebot_plugin_ts3_tracker.models import Ts3OnlineUser, Ts3ServerStatus
from nonebot_plugin_ts3_tracker.runtime import Ts3TrackerRuntime
from nonebot_plugin_ts3_tracker.service import Ts3TrackerService
from nonebot_plugin_ts3_tracker.storage import SnapshotStore


class SequenceClient:
    def __init__(self, statuses: list[Ts3ServerStatus]) -> None:
        self._statuses = statuses
        self._index = 0

    async def fetch_status(self) -> Ts3ServerStatus:
        result = self._statuses[min(self._index, len(self._statuses) - 1)]
        self._index += 1
        return result


class SequenceNow:
    def __init__(self, timestamps: list[datetime]) -> None:
        self._timestamps = timestamps
        self._index = 0

    def __call__(self) -> datetime:
        value = self._timestamps[min(self._index, len(self._timestamps) - 1)]
        self._index += 1
        return value


def build_settings(tmp_path, **overrides: object) -> Ts3TrackerSettings:
    base = {
        "server_host": "127.0.0.1",
        "server_port": 9987,
        "serverquery_port": 10011,
        "serverquery_username": "query-user",
        "serverquery_password": "password",
        "notification_enabled": True,
        "notify_target_groups": "123456",
        "data_dir": str(tmp_path),
    }
    base.update(overrides)
    return Ts3TrackerSettings(**base)


def build_status(user_names: list[str]) -> Ts3ServerStatus:
    users = [
        Ts3OnlineUser(
            nickname=name,
            channel_id="1",
            channel_name="APEX",
            client_id=str(index),
            database_id=str(index),
            unique_id=f"uid-{name}",
            client_ip="127.0.0.1",
            connected_duration_seconds=120,
            away=False,
        )
        for index, name in enumerate(user_names, start=1)
    ]
    return Ts3ServerStatus(
        server_name="Test TS3",
        server_host="127.0.0.1",
        server_port=9987,
        online_count=len(users),
        channels=[("1", "APEX")],
        users=users,
    )


@pytest.mark.asyncio
async def test_runtime_first_sync_is_silent(tmp_path) -> None:
    sent: list[tuple[str, str, str]] = []
    settings = build_settings(tmp_path)
    service = Ts3TrackerService(
        settings,
        client_factory=lambda: SequenceClient([build_status(["neri"])]),  # type: ignore[arg-type]
    )
    runtime = Ts3TrackerRuntime(
        settings,
        service,
        store=SnapshotStore(tmp_path / "snapshot.json"),
        message_sender=lambda target_type, target, message: _record_send(  # type: ignore[arg-type]
            sent, target_type, target, message
        ),
        now_factory=lambda: datetime(2026, 3, 16, 14, 30, 0),
    )

    diff = await runtime.sync_once(notify=False)
    assert [item.nickname for item in diff.joined] == ["neri"]
    assert sent == []


@pytest.mark.asyncio
async def test_runtime_detects_join_and_leave_and_sends_notifications(
    tmp_path,
) -> None:
    sent: list[tuple[str, str, str]] = []
    settings = build_settings(tmp_path)
    sequence_client = SequenceClient(
        [
            build_status(["neri"]),
            build_status(["KirA", "neri"]),
            build_status(["KirA"]),
        ]
    )
    service = Ts3TrackerService(
        settings,
        client_factory=lambda: sequence_client,  # type: ignore[arg-type]
    )
    now_factory = SequenceNow(
        [
            datetime(2026, 3, 16, 14, 28, 0),
            datetime(2026, 3, 16, 14, 29, 0),
            datetime(2026, 3, 16, 14, 30, 0),
            datetime(2026, 3, 16, 14, 30, 0),
            datetime(2026, 3, 16, 14, 30, 0),
        ]
    )

    runtime = Ts3TrackerRuntime(
        settings,
        service,
        store=SnapshotStore(tmp_path / "snapshot.json"),
        message_sender=lambda target_type, target, message: _record_send(  # type: ignore[arg-type]
            sent, target_type, target, message
        ),
        now_factory=now_factory,
    )

    await runtime.sync_once(notify=False)
    second = await runtime.sync_once(notify=True)
    third = await runtime.sync_once(notify=True)

    assert [item.nickname for item in second.joined] == ["KirA"]
    assert second.left == []
    assert third.joined == []
    assert [item.nickname for item in third.left] == ["neri"]
    assert len(sent) == 2
    assert sent[0][0] == "group"
    assert sent[0][1] == "123456"
    assert "让我看看是谁还没上号 👀" in sent[0][2]
    assert "🧾 昵称：KirA" in sent[0][2]
    assert "📣 KirA 进入了 TS 服务器" in sent[0][2]
    assert "📤 用户下线通知" in sent[1][2]
    assert "🧾 昵称：neri" in sent[1][2]
    assert "⏱️ 在线时长：2分0秒" in sent[1][2]


async def _record_send(
    sent: list[tuple[str, str, str]], target_type: str, target: str, message: str
) -> bool:
    sent.append((target_type, target, message))
    return True
