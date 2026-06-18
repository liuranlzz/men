from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import load_config, load_json, write_json
from .deepseek import structure_with_deepseek
from .draft_writer import write_jianying_draft
from .models import Manifest
from .parser import parse_script_markdown
from .subtitle import build_subtitles, write_srt
from .utils import now_stamp, sanitize_filename


def main(argv: Optional[List[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    config = load_config(args.config)
    if args.draft_root:
        config["jianying_draft_root"] = args.draft_root

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    manifest = load_manifest(input_path, args.input_format, config)

    if args.ai_provider == "deepseek":
        markdown_text = input_path.read_text(encoding="utf-8")
        manifest = structure_with_deepseek(markdown_text, manifest, config)

    draft_name = sanitize_filename(args.draft_name or f"{manifest.project_name}-{now_stamp()}")
    output_root = Path(args.output_dir)
    run_dir = output_root / draft_name
    run_dir.mkdir(parents=True, exist_ok=True)

    subtitles = build_subtitles(manifest, str(config.get("caption_split", "segment")))
    manifest_path = run_dir / "manifest.json"
    srt_path = run_dir / "captions.srt"
    write_json(manifest_path, manifest.to_dict())
    write_srt(srt_path, subtitles)
    write_scene_notes(run_dir / "scene_notes.md", manifest)

    result: Dict[str, Any] = {
        "draft_name": draft_name,
        "run_dir": str(run_dir),
        "manifest": str(manifest_path),
        "captions": str(srt_path),
        "subtitle_count": len(subtitles),
        "duration": manifest.duration,
        "dry_run": bool(args.dry_run),
    }

    if not args.dry_run:
        if args.allow_replace:
            config["allow_replace"] = True
        draft_path = write_jianying_draft(manifest, srt_path, draft_name, config)
        result["jianying_draft_path"] = str(draft_path)

    write_json(run_dir / "run.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="JianyingGo",
        description="Generate editable Jianying drafts from short-video scripts.",
    )
    parser.add_argument("--input", required=True, help="Markdown script or manifest JSON.")
    parser.add_argument(
        "--input-format",
        choices=["md", "manifest"],
        default="md",
        help="Input format. Default: md.",
    )
    parser.add_argument("--config", help="JSON config file. Defaults are built in.")
    parser.add_argument(
        "--output-dir",
        default="out",
        help="Local output directory for manifest, SRT, and logs.",
    )
    parser.add_argument("--draft-name", help="Jianying draft name.")
    parser.add_argument(
        "--draft-root",
        help="Override Jianying draft root. Useful for local tests.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not write Jianying draft.")
    parser.add_argument(
        "--allow-replace",
        action="store_true",
        help="Allow replacing an existing Jianying draft with the same name.",
    )
    parser.add_argument(
        "--ai-provider",
        choices=["none", "deepseek"],
        default="none",
        help="Optional AI structuring provider.",
    )
    return parser


def load_manifest(input_path: Path, input_format: str, config: Dict[str, Any]) -> Manifest:
    if input_format == "manifest":
        return Manifest.from_dict(load_json(input_path))
    return parse_script_markdown(input_path, canvas=config.get("canvas"))


def write_scene_notes(path: Path, manifest: Manifest) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {manifest.project_name}\n\n")
        for seg in manifest.segments:
            f.write(f"## {seg.index + 1}. {seg.start:g}-{seg.end:g}s {seg.scene_title}\n\n")
            if seg.visual_note:
                f.write(f"- 画面：{seg.visual_note}\n")
            if seg.voice_role:
                f.write(f"- 配音：{seg.voice_role}\n")
            f.write(f"- 文本：{seg.voice_text}\n\n")
