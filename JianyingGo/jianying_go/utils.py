from __future__ import annotations

import base64
import re
import unicodedata
from datetime import datetime
from pathlib import Path


WHITE_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMA"
    "ASsJTYQAAAAASUVORK5CYII="
)


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def sanitize_filename(name: str, fallback: str = "jianying_draft", max_len: int = 120) -> str:
    name = unicodedata.normalize("NFKC", name or "").strip()
    if not name:
        name = fallback
    name = re.sub(r"[\\/:*?\"<>|\r\n\t]+", "-", name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    if not name:
        name = fallback
    while len(name.encode("utf-8")) > max_len:
        name = name[:-1]
    return name or fallback


def strip_markdown(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = text.strip()
    text = text.strip("“”\"' ")
    return re.sub(r"\s+", " ", text).strip()


def ensure_white_png(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size == 0:
        path.write_bytes(base64.b64decode(WHITE_PNG_BASE64))
    return path


def seconds_to_us(seconds: float) -> int:
    return int(round(seconds * 1_000_000))
