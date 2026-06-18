from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict

from .models import Manifest


def structure_with_deepseek(markdown_text: str, local_manifest: Manifest, config: Dict[str, Any]) -> Manifest:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is not set")

    deepseek_config = config.get("deepseek", {})
    base_url = str(deepseek_config.get("base_url", "https://api.deepseek.com")).rstrip("/")
    model = str(deepseek_config.get("model", "deepseek-v4-flash"))
    endpoint = f"{base_url}/chat/completions"

    prompt = {
        "task": "Normalize a short-video markdown script into strict JSON.",
        "rules": [
            "Keep the original start/end times unless they are obviously missing.",
            "Keep every voice_text faithful to the original script.",
            "caption_text should be suitable for Jianying subtitles.",
            "Return only JSON with project_name, canvas, segments.",
        ],
        "local_manifest": local_manifest.to_dict(),
        "markdown": markdown_text,
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You convert Chinese short-video scripts into strict JSON manifests.",
            },
            {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
        ],
        "response_format": {"type": "json_object"},
        "thinking": {"type": str(deepseek_config.get("thinking", "disabled"))},
        "stream": False,
    }

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DeepSeek request failed: HTTP {exc.code}: {body}") from exc

    content = data["choices"][0]["message"]["content"]
    structured = json.loads(content)
    if not structured.get("source_path"):
        structured["source_path"] = local_manifest.source_path
    return Manifest.from_dict(structured)
