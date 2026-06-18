from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union


DEFAULT_CONFIG: Dict[str, Any] = {
    "jianying_draft_root": "~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft",
    "allow_replace": False,
    "fps": 30,
    "canvas": {"width": 1080, "height": 1920},
    "caption_split": "segment",
    "subtitle": {
        "track_name": "subtitles",
        "size": 8.0,
        "transform_y": -0.78,
        "color": [1.0, 1.0, 1.0],
        "border_color": [0.0, 0.0, 0.0],
        "border_width": 45.0,
        "shadow_alpha": 0.25,
        "shadow_color": [0.0, 0.0, 0.0],
        "shadow_diffuse": 18.0,
        "shadow_distance": 6.0,
        "shadow_angle": -45.0,
        "max_line_width": 0.86,
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-v4-flash",
        "thinking": "disabled",
    },
}


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: Optional[str]) -> Dict[str, Any]:
    config = DEFAULT_CONFIG
    if path:
        with open(path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        config = deep_merge(DEFAULT_CONFIG, user_config)

    root = str(config.get("jianying_draft_root", "")).strip()
    if root:
        config["jianying_draft_root"] = os.path.expanduser(root)

    return config


def load_json(path: Union[str, Path]) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Union[str, Path], data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
