from __future__ import annotations

from nonebot.compat import BaseModel, field_validator


class Ts3TrackerSettings(BaseModel):
    server_host: str = ""
    server_port: int = 9987
    serverquery_port: int = 10011
    serverquery_username: str = ""
    serverquery_password: str = ""
    debug: bool = False
    command_prefix_required: bool = True
    query_timeout_seconds: float = 10.0
    notification_enabled: bool = False
    notify_target_groups: str = ""
    notify_target_users: str = ""
    group_whitelist_enabled: bool = False
    group_whitelist_groups: str = ""
    poll_interval_seconds: int = 5
    startup_silent: bool = True
    data_dir: str = ""

    @field_validator(
        "server_host",
        "serverquery_username",
        "serverquery_password",
        "notify_target_groups",
        "notify_target_users",
        "group_whitelist_groups",
        "data_dir",
        mode="before",
    )
    @classmethod
    def strip_text(cls, value: object) -> str:
        return str(value).strip()

    @field_validator("poll_interval_seconds")
    @classmethod
    def validate_positive_int(cls, value: int) -> int:
        return max(1, value)

    @field_validator("query_timeout_seconds")
    @classmethod
    def validate_timeout(cls, value: float) -> float:
        return max(1.0, value)

    def parse_targets(self, raw: str) -> list[str]:
        normalized = raw.replace("\r", "\n").replace(";", "\n").replace(",", "\n")
        targets = [item.strip() for item in normalized.split("\n")]
        return [item for item in targets if item]

    def is_group_allowed(self, group_id: str | int | None) -> bool:
        if group_id is None or not self.group_whitelist_enabled:
            return True
        return str(group_id) in set(self.parse_targets(self.group_whitelist_groups))

    def get_effective_notify_groups(self) -> list[str]:
        notify_groups = self.get_notify_groups()
        return self.filter_groups_by_whitelist(notify_groups)

    def get_notify_groups(self) -> list[str]:
        return self.parse_targets(self.notify_target_groups)

    def filter_groups_by_whitelist(self, group_ids: list[str]) -> list[str]:
        if not self.group_whitelist_enabled:
            return group_ids
        whitelist = set(self.parse_targets(self.group_whitelist_groups))
        return [group_id for group_id in group_ids if group_id in whitelist]


class Config(BaseModel):
    ts3_tracker: Ts3TrackerSettings = Ts3TrackerSettings()
