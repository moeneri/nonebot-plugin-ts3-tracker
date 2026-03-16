from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import nonebot

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

nonebot.init()

from nonebot_plugin_ts3_tracker.config import Ts3TrackerSettings
from nonebot_plugin_ts3_tracker.service import Ts3TrackerService


def build_settings() -> Ts3TrackerSettings:
    return Ts3TrackerSettings(
        server_host=os.getenv("TS3_TRACKER__SERVER_HOST", ""),
        server_port=int(os.getenv("TS3_TRACKER__SERVER_PORT", "9987")),
        serverquery_port=int(os.getenv("TS3_TRACKER__SERVERQUERY_PORT", "10011")),
        serverquery_username=os.getenv("TS3_TRACKER__SERVERQUERY_USERNAME", ""),
        serverquery_password=os.getenv("TS3_TRACKER__SERVERQUERY_PASSWORD", ""),
        debug=os.getenv("TS3_TRACKER__DEBUG", "false").lower() == "true",
        query_timeout_seconds=float(
            os.getenv("TS3_TRACKER__QUERY_TIMEOUT_SECONDS", "10")
        ),
    )


async def main() -> None:
    service = Ts3TrackerService(build_settings())
    print(await service.build_server_message())


if __name__ == "__main__":
    asyncio.run(main())
