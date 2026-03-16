from __future__ import annotations

import nonebot
import pytest
from nonebot.adapters.onebot.v11 import Adapter

nonebot.init()
driver = nonebot.get_driver()
try:
    driver.register_adapter(Adapter)
except ValueError:
    pass


@pytest.fixture(scope="session", autouse=True)
def init_nonebot() -> None:
    return None
