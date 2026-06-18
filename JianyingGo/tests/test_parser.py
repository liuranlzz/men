import tempfile
import unittest
from pathlib import Path

from jianying_go.parser import parse_script_markdown
from jianying_go.subtitle import build_subtitles


SAMPLE = """#### 【0-6秒】 黄金开头

- **画面**：实拍手部特写。
- **知性女声**：
    “新配的卷帘门遥控器，按键功能全乱了？千万别扔！”

#### 【7-13秒】 核心认知

- **画面**：线路板特写。
- **知性女声**：
    “乱套是因为芯片里有四个数据脚，不同厂家连线不一样。”
"""


class ParserTest(unittest.TestCase):
    def test_parse_script_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.md"
            path.write_text(SAMPLE, encoding="utf-8")
            manifest = parse_script_markdown(path)

        self.assertEqual(manifest.project_name, "sample")
        self.assertEqual(len(manifest.segments), 2)
        self.assertEqual(manifest.segments[0].start, 0.0)
        self.assertEqual(manifest.segments[0].end, 6.0)
        self.assertIn("卷帘门遥控器", manifest.segments[0].voice_text)

    def test_build_segment_subtitles(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.md"
            path.write_text(SAMPLE, encoding="utf-8")
            manifest = parse_script_markdown(path)
            subtitles = build_subtitles(manifest, "segment")

        self.assertEqual(len(subtitles), 2)
        self.assertEqual(subtitles[1].start, 7.0)
        self.assertEqual(subtitles[1].end, 13.0)


if __name__ == "__main__":
    unittest.main()
