from __future__ import annotations

from pathlib import Path

from nonebot import require

from ts3_tracker_shared.runtime import Ts3TrackerRuntime as BaseTs3TrackerRuntime


class Ts3TrackerRuntime(BaseTs3TrackerRuntime):
    def _build_snapshot_file(self) -> Path:
        if self.settings.data_dir:
            return Path(self.settings.data_dir) / "snapshot.json"

        require("nonebot_plugin_localstore")
        import nonebot_plugin_localstore as store

        return store.get_plugin_data_file("snapshot.json")

    def _build_group_notify_file(self) -> Path:
        if self.settings.data_dir:
            return Path(self.settings.data_dir) / "group_notify.json"

        require("nonebot_plugin_localstore")
        import nonebot_plugin_localstore as store

        return store.get_plugin_data_file("group_notify.json")
