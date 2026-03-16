from __future__ import annotations

from pathlib import Path

from nonebot_plugin_ts3_tracker.storage import SnapshotStore, TrackedClientSnapshot


def test_snapshot_store_roundtrip(tmp_path: Path) -> None:
    store = SnapshotStore(tmp_path / "snapshot.json")
    snapshots = {
        "uid:1": TrackedClientSnapshot(
            nickname="Alice",
            unique_id="uid-1",
            channel_id="1",
            channel_name="APEX",
            connected_duration_seconds=12,
            away=False,
            first_seen_at="2026-03-16 16:00:00",
        )
    }
    store.save(snapshots)

    loaded = store.load()
    assert loaded["uid:1"].nickname == "Alice"
    assert loaded["uid:1"].channel_name == "APEX"
    assert loaded["uid:1"].first_seen_at == "2026-03-16 16:00:00"
