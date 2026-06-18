# 架构说明

JianyingGo 分成五层：

```text
Markdown 口稿
  -> parser.py
  -> Manifest
  -> subtitle.py
  -> captions.srt
  -> draft_writer.py
  -> 剪映草稿目录
```

## 模块

- `create_draft.py`：命令入口
- `jianying_go/cli.py`：参数解析和总流程
- `jianying_go/parser.py`：解析项目口稿 Markdown
- `jianying_go/subtitle.py`：生成 SRT 字幕
- `jianying_go/draft_writer.py`：调用 `pyJianYingDraft` 写入草稿
- `jianying_go/deepseek.py`：可选 DeepSeek 结构化增强
- `jianying_go/models.py`：Manifest 和 Segment 数据结构
- `jianying_go/config.py`：配置加载

## 数据结构

核心中间产物是 `Manifest`：

```json
{
  "project_name": "遥控4.0内容",
  "canvas": {
    "width": 1080,
    "height": 1920
  },
  "segments": [
    {
      "index": 0,
      "start": 0.0,
      "end": 6.0,
      "scene_title": "黄金开头：痛点展示",
      "visual_note": "实拍手部特写...",
      "voice_role": "知性女声",
      "voice_text": "新配的卷帘门遥控器...",
      "caption_text": "新配的卷帘门遥控器..."
    }
  ]
}
```

只要后续 Coze 或其他工具能输出这个结构，就可以复用同一套草稿生成逻辑。

## 当前边界

第一版不做：

- 外部 TTS 自动生成音频
- 自动导出 MP4
- 高版本剪映模板读取和替换
- 复杂贴纸、花字、转场复刻

第一版专注：

- 可打开草稿
- 可编辑字幕文本
- 字幕样式可控
- 适合剪映会员手动文本朗读

