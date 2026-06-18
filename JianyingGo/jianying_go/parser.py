from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from .models import Manifest, Segment
from .utils import sanitize_filename, strip_markdown


HEADING_RE = re.compile(
    r"^\s*#{1,6}\s*【\s*([0-9]+(?:\.[0-9]+)?)\s*[-~—到]\s*([0-9]+(?:\.[0-9]+)?)\s*秒\s*】\s*(.*)$"
)
FIELD_RE = re.compile(r"^\s*-\s*\*\*(.+?)\*\*\s*[:：]\s*(.*)$")


def parse_script_markdown(
    path: Union[str, Path], canvas: Optional[Dict[str, int]] = None
) -> Manifest:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    blocks = _split_blocks(text)
    segments: List[Segment] = []

    for index, (start, end, title, body) in enumerate(blocks):
        visual_note, voice_role, voice_text = _extract_fields(body)
        segments.append(
            Segment(
                index=index,
                start=start,
                end=end,
                scene_title=strip_markdown(title),
                visual_note=visual_note,
                voice_role=voice_role,
                voice_text=voice_text,
                caption_text=voice_text,
            )
        )

    if not segments:
        raise ValueError(f"No timed sections found in markdown: {source}")

    return Manifest(
        project_name=sanitize_filename(source.stem),
        source_path=str(source),
        canvas={
            "width": int((canvas or {}).get("width", 1080)),
            "height": int((canvas or {}).get("height", 1920)),
        },
        segments=segments,
    )


def _split_blocks(text: str) -> List[Tuple[float, float, str, List[str]]]:
    lines = text.splitlines()
    blocks: List[Tuple[float, float, str, List[str]]] = []
    current = None

    for line in lines:
        match = HEADING_RE.match(line)
        if match:
            if current is not None:
                blocks.append(current)
            start = float(match.group(1))
            end = float(match.group(2))
            title = match.group(3).strip()
            current = (start, end, title, [])
            continue
        if current is not None:
            current[3].append(line)

    if current is not None:
        blocks.append(current)
    return blocks


def _extract_fields(lines: List[str]) -> Tuple[str, str, str]:
    fields: List[Tuple[str, List[str]]] = []
    current_key = None
    current_value: List[str] = []

    def flush() -> None:
        nonlocal current_key, current_value
        if current_key is not None:
            fields.append((current_key, current_value))
        current_key = None
        current_value = []

    for line in lines:
        match = FIELD_RE.match(line)
        if match:
            flush()
            current_key = strip_markdown(match.group(1))
            inline = strip_markdown(match.group(2))
            current_value = [inline] if inline else []
            continue

        if current_key is not None:
            clean = strip_markdown(line)
            if clean:
                current_value.append(clean)

    flush()

    visual_note = ""
    voice_role = ""
    voice_text = ""

    for key, value_lines in fields:
        value = strip_markdown(" ".join(value_lines))
        if not value:
            continue
        if key == "画面":
            visual_note = value
        elif not voice_text:
            voice_role = key
            voice_text = value

    if not voice_text:
        raise ValueError("Timed section is missing a voice text field")

    return visual_note, voice_role, voice_text
