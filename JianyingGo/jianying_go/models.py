from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Segment:
    index: int
    start: float
    end: float
    scene_title: str = ""
    visual_note: str = ""
    voice_role: str = ""
    voice_text: str = ""
    caption_text: str = ""

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "start": self.start,
            "end": self.end,
            "scene_title": self.scene_title,
            "visual_note": self.visual_note,
            "voice_role": self.voice_role,
            "voice_text": self.voice_text,
            "caption_text": self.caption_text,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], index: Optional[int] = None) -> "Segment":
        idx = data.get("index", index if index is not None else 0)
        start = float(data.get("start", 0.0))
        end = float(data.get("end", start))
        voice_text = str(data.get("voice_text", "")).strip()
        caption_text = str(data.get("caption_text") or voice_text).strip()
        return cls(
            index=int(idx),
            start=start,
            end=end,
            scene_title=str(data.get("scene_title", "")).strip(),
            visual_note=str(data.get("visual_note", "")).strip(),
            voice_role=str(data.get("voice_role", "")).strip(),
            voice_text=voice_text,
            caption_text=caption_text,
        )


@dataclass
class Manifest:
    project_name: str
    source_path: str = ""
    canvas: Dict[str, int] = field(default_factory=lambda: {"width": 1080, "height": 1920})
    segments: List[Segment] = field(default_factory=list)

    @property
    def duration(self) -> float:
        if not self.segments:
            return 0.0
        return max(seg.end for seg in self.segments)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "source_path": self.source_path,
            "canvas": self.canvas,
            "duration": self.duration,
            "segments": [seg.to_dict() for seg in self.segments],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Manifest":
        segments = [
            Segment.from_dict(seg, index=i)
            for i, seg in enumerate(data.get("segments", []))
        ]
        canvas = data.get("canvas") or {"width": 1080, "height": 1920}
        return cls(
            project_name=str(data.get("project_name") or "jianying_draft").strip(),
            source_path=str(data.get("source_path", "")).strip(),
            canvas={
                "width": int(canvas.get("width", 1080)),
                "height": int(canvas.get("height", 1920)),
            },
            segments=segments,
        )
