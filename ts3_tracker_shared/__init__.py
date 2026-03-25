from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_SOURCE_DIR = Path(__file__).resolve().parent.parent / "nonebot_plugin_ts3_tracker"
_MODULES = ("models", "query", "storage", "config", "service", "runtime")


def _load_module(name: str) -> None:
    module_name = f"{__name__}.{name}"
    if module_name in sys.modules:
        return

    source_path = _SOURCE_DIR / f"{name}.py"
    spec = spec_from_file_location(module_name, source_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load shared module: {module_name}")

    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)


for _module_name in _MODULES:
    _load_module(_module_name)


__all__ = list(_MODULES)
