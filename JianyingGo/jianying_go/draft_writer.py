from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict

from .models import Manifest


def write_jianying_draft(
    manifest: Manifest,
    srt_path: Path,
    draft_name: str,
    config: Dict[str, Any],
) -> Path:
    try:
        import pyJianYingDraft as draft
        from pyJianYingDraft import ClipSettings, trange
        from pyJianYingDraft.text_segment import (
            TextBorder,
            TextSegment,
            TextShadow,
            TextStyle,
        )
    except ImportError as exc:
        raise RuntimeError(
            "pyJianYingDraft is not installed. Run: pip install -r requirements.txt"
        ) from exc

    draft_root = Path(config["jianying_draft_root"]).expanduser()
    if not draft_root.exists():
        raise FileNotFoundError(f"Jianying draft root does not exist: {draft_root}")

    width = int(config.get("canvas", {}).get("width", manifest.canvas.get("width", 1080)))
    height = int(config.get("canvas", {}).get("height", manifest.canvas.get("height", 1920)))
    fps = int(config.get("fps", 30))
    allow_replace = bool(config.get("allow_replace", False))

    folder = draft.DraftFolder(str(draft_root))
    script = folder.create_draft(draft_name, width, height, fps, allow_replace=allow_replace)

    subtitle_config = config.get("subtitle", {})
    text_style = _make_text_style(TextStyle, subtitle_config)
    border = _make_border(TextBorder, subtitle_config)
    shadow = _make_shadow(TextShadow, subtitle_config)
    clip_settings = ClipSettings(
        transform_y=float(subtitle_config.get("transform_y", -0.78))
    )

    style_ref = TextSegment(
        "template",
        trange(0, 1_000_000),
        style=text_style,
        border=border,
        shadow=shadow,
        clip_settings=clip_settings,
    )

    track_name = str(subtitle_config.get("track_name", "subtitles"))
    script.import_srt(
        str(srt_path),
        track_name=track_name,
        style_reference=style_ref,
        clip_settings=clip_settings,
    )
    script.save()

    draft_path = draft_root / draft_name
    _write_extra_project_files(draft_path)
    return draft_path


def _make_text_style(TextStyle: Any, subtitle_config: Dict[str, Any]) -> Any:
    kwargs = {
        "size": float(subtitle_config.get("size", 8.0)),
        "align": int(subtitle_config.get("align", 1)),
        "auto_wrapping": bool(subtitle_config.get("auto_wrapping", True)),
        "color": tuple(subtitle_config.get("color", [1.0, 1.0, 1.0])),
    }
    if "max_line_width" in subtitle_config:
        kwargs["max_line_width"] = float(subtitle_config["max_line_width"])
    try:
        return TextStyle(**kwargs)
    except TypeError:
        kwargs.pop("max_line_width", None)
        return TextStyle(**kwargs)


def _make_border(TextBorder: Any, subtitle_config: Dict[str, Any]) -> Any:
    width = float(subtitle_config.get("border_width", 0.0))
    if width <= 0:
        return None
    return TextBorder(
        alpha=1.0,
        color=tuple(subtitle_config.get("border_color", [0.0, 0.0, 0.0])),
        width=width,
    )


def _make_shadow(TextShadow: Any, subtitle_config: Dict[str, Any]) -> Any:
    alpha = float(subtitle_config.get("shadow_alpha", 0.0))
    if alpha <= 0:
        return None
    return TextShadow(
        alpha=alpha,
        color=tuple(subtitle_config.get("shadow_color", [0.0, 0.0, 0.0])),
        diffuse=float(subtitle_config.get("shadow_diffuse", 18.0)),
        distance=float(subtitle_config.get("shadow_distance", 6.0)),
        angle=float(subtitle_config.get("shadow_angle", -45.0)),
    )


def _write_extra_project_files(draft_path: Path) -> None:
    content_path = draft_path / "draft_content.json"
    if not content_path.exists():
        return

    info_path = draft_path / "draft_info.json"
    if not info_path.exists():
        shutil.copy2(content_path, info_path)

    layout_path = draft_path / "timeline_layout.json"
    if not layout_path.exists():
        with open(content_path, "r", encoding="utf-8") as f:
            content = json.load(f)
        timeline_id = content.get("id", "")
        layout = {
            "dockItems": [
                {
                    "dockIndex": 0,
                    "ratio": 1,
                    "timelineIds": [timeline_id],
                    "timelineNames": ["时间线01"],
                }
            ],
            "layoutOrientation": 1,
        }
        with open(layout_path, "w", encoding="utf-8") as f:
            json.dump(layout, f, ensure_ascii=False, indent=2)
