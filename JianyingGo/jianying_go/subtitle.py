from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Union

from .models import Manifest, Segment
from .utils import strip_markdown


@dataclass
class SubtitleItem:
    index: int
    start: float
    end: float
    text: str


def build_subtitles(manifest: Manifest, split_mode: str = "segment") -> List[SubtitleItem]:
    items: List[SubtitleItem] = []
    for segment in manifest.segments:
        if split_mode == "sentence":
            items.extend(_split_segment_by_sentence(segment, len(items)))
        else:
            text = strip_markdown(segment.caption_text or segment.voice_text)
            items.append(SubtitleItem(len(items) + 1, segment.start, segment.end, text))

    for idx, item in enumerate(items, start=1):
        item.index = idx
    return items


def write_srt(path: Union[str, Path], subtitles: Iterable[SubtitleItem]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for item in subtitles:
            f.write(f"{item.index}\n")
            f.write(f"{_format_srt_time(item.start)} --> {_format_srt_time(item.end)}\n")
            f.write(f"{item.text}\n\n")


def _split_segment_by_sentence(segment: Segment, offset: int) -> List[SubtitleItem]:
    text = strip_markdown(segment.caption_text or segment.voice_text)
    parts = _sentence_parts(text)
    if len(parts) <= 1 or segment.duration <= 0:
        return [SubtitleItem(offset + 1, segment.start, segment.end, text)]

    total_weight = sum(max(1, len(part)) for part in parts)
    cursor = segment.start
    items: List[SubtitleItem] = []
    for idx, part in enumerate(parts):
        if idx == len(parts) - 1:
            end = segment.end
        else:
            share = max(1, len(part)) / total_weight
            end = min(segment.end, cursor + segment.duration * share)
        items.append(SubtitleItem(offset + idx + 1, cursor, end, part))
        cursor = end
    return items


def _sentence_parts(text: str) -> List[str]:
    pieces = re.split(r"(?<=[。！？!?；;])\s*", text)
    pieces = [piece.strip() for piece in pieces if piece.strip()]
    if len(pieces) > 1:
        return pieces
    comma_pieces = re.split(r"(?<=[，,、])\s*", text)
    return [piece.strip() for piece in comma_pieces if piece.strip()]


def _format_srt_time(seconds: float) -> str:
    millis = max(0, int(round(seconds * 1000)))
    hours, rem = divmod(millis, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"
