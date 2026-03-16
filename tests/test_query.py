from __future__ import annotations

from nonebot_plugin_ts3_tracker.query import Ts3QueryClient, Ts3QueryError


def build_client() -> Ts3QueryClient:
    return Ts3QueryClient(
        host="127.0.0.1",
        server_port=9987,
        query_port=10011,
        username="query-user",
        password="password",
    )


def test_escape_and_unescape() -> None:
    client = build_client()
    original = "A B/C|D\\E\n"
    escaped = client._escape(original)
    assert escaped == "A\\sB\\/C\\pD\\\\E\\n"
    assert client._unescape(escaped) == original


def test_parse_response_success() -> None:
    client = build_client()
    records = client._parse_response(
        [
            "cid=1 channel_name=APEX total_clients=2|cid=2 channel_name=原神 total_clients=0",
            "error id=0 msg=ok",
        ],
        "channellist",
    )
    assert records == [
        {"cid": "1", "channel_name": "APEX", "total_clients": "2"},
        {"cid": "2", "channel_name": "原神", "total_clients": "0"},
    ]


def test_parse_response_error() -> None:
    client = build_client()
    try:
        client._parse_response(
            ["error id=2568 msg=insufficient\\sclient\\spermissions"],
            "clientlist",
        )
    except Ts3QueryError as exc:
        assert "clientlist 失败" in str(exc)
        assert "insufficient client permissions" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected Ts3QueryError")
