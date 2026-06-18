# JianyingGo

从项目口稿 Markdown 生成可打开的剪映草稿。

第一版定位是“半自动剪映工作流”：

- 自动解析口稿时间轴、画面说明、口播文本
- 自动生成 `manifest.json`
- 自动生成 `captions.srt`
- 自动写入剪映草稿字幕轨
- 字幕字号、位置、颜色、描边、阴影可配置
- 配音不走外部 TTS，打开剪映后用会员账号手动执行“文本朗读 / AI 配音”

## 为什么先做半自动

你已经有剪映会员账号，所以最稳的流程是让本工具负责“草稿和字幕”，剪映负责“会员音色配音”。

这样可以避开外部 TTS API、音频授权、音色质量、配音时长对齐等问题。等字幕草稿稳定后，再考虑接外部 TTS 或 Coze。

## 安装

进入工具目录：

```bash
cd JianyingGo
```

建议创建虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

核心依赖：

```text
pyJianYingDraft
```

如果暂时不安装依赖，也可以先用 `--dry-run` 验证口稿解析和字幕生成。

## 快速验证

只生成本地调试产物，不写剪映草稿：

```bash
python create_draft.py \
  --input "../content/遥控4.0/遥控4.0内容.md" \
  --config "config.example.json" \
  --dry-run
```

产物示例：

```text
out/遥控4.0内容-20260617-123456/
  manifest.json
  captions.srt
  scene_notes.md
  run.json
```

## 生成剪映草稿

先确认 `config.example.json` 里的剪映草稿目录正确：

```json
{
  "jianying_draft_root": "~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
}
```

macOS 常见路径就是上面这个。如果你的剪映草稿位置改过，请在剪映设置里查看草稿位置，然后改配置。

执行：

```bash
python create_draft.py \
  --input "../content/遥控4.0/遥控4.0内容.md" \
  --config "config.example.json" \
  --draft-name "遥控4.0-字幕草稿"
```

如果同名草稿已存在，可以显式覆盖：

```bash
python create_draft.py \
  --input "../content/遥控4.0/遥控4.0内容.md" \
  --config "config.example.json" \
  --draft-name "遥控4.0-字幕草稿" \
  --allow-replace
```

执行成功后，打开剪映，在草稿列表里找到 `遥控4.0-字幕草稿`。

如果只想测试真实写草稿，但不写入剪映目录，可以覆盖草稿根目录：

```bash
mkdir -p out/local_drafts
python create_draft.py \
  --input "../content/遥控4.0/遥控4.0内容.md" \
  --config "config.example.json" \
  --draft-root "out/local_drafts" \
  --draft-name "local-test" \
  --allow-replace
```

## 剪映内手动配音流程

1. 打开生成的草稿
2. 检查字幕位置和字号
3. 选中字幕文本片段
4. 使用剪映的“文本朗读 / AI 配音”
5. 选择会员音色
6. 生成配音音频
7. 根据配音实际节奏微调文本片段或音频片段
8. 补充画面素材并导出

建议第一版使用 `caption_split: "segment"`，即每个口稿段落生成一个字幕片段。这样在剪映里手动文本朗读更省事。

如果想让字幕观看体验更细，可以改成：

```json
{
  "caption_split": "sentence"
}
```

这会按句子拆字幕，但手动朗读时操作会更多。

## 输入格式

当前支持这种 Markdown 口稿：

```markdown
#### 【0-6秒】 黄金开头：痛点展示

- **画面**：实拍手部特写。按下遥控器“上升”，结果卷帘门往下走。
- **知性女声**：
    “新配的卷帘门遥控器，按键功能全乱了？千万别扔！”
```

工具会提取：

- `0-6秒`：时间轴
- `黄金开头：痛点展示`：段落标题
- `画面`：画面说明，写入 `scene_notes.md`
- `知性女声`：配音角色
- 引号里的文本：字幕文本

## 配置说明

`config.example.json` 里最常改的是：

```json
{
  "caption_split": "segment",
  "subtitle": {
    "size": 8.0,
    "transform_y": -0.78,
    "color": [1.0, 1.0, 1.0],
    "border_color": [0.0, 0.0, 0.0],
    "border_width": 45.0,
    "max_line_width": 0.86
  }
}
```

字段含义：

- `caption_split`：`segment` 按段落生成；`sentence` 按句子拆分
- `subtitle.size`：剪映内部字号，不是像素，需要实际校准
- `subtitle.transform_y`：字幕纵向位置，底部字幕可从 `-0.70` 到 `-0.85` 试
- `subtitle.color`：RGB，范围 `0.0-1.0`
- `subtitle.border_width`：描边粗细
- `subtitle.max_line_width`：自动换行宽度

## DeepSeek 可选增强

DeepSeek 不能直接生成配音音频，但可以用来整理口稿和拆字幕。

设置环境变量：

```bash
export DEEPSEEK_API_KEY="你的 key"
```

运行：

```bash
python create_draft.py \
  --input "../content/遥控4.0/遥控4.0内容.md" \
  --config "config.example.json" \
  --ai-provider deepseek \
  --dry-run
```

建议先 `--dry-run` 看 `manifest.json` 是否符合预期，再真正写入草稿。

## 常见问题

### 1. 找不到剪映草稿目录

检查 `config.example.json` 的 `jianying_draft_root`。如果剪映草稿位置不是默认目录，需要改成你的真实路径。

### 2. `pyJianYingDraft is not installed`

在 `JianyingGo` 目录执行：

```bash
pip install -r requirements.txt
```

### 3. 字幕位置不对

改 `subtitle.transform_y`，然后用 `--allow-replace` 重新生成草稿。

### 4. 字幕太大或太小

改 `subtitle.size`。剪映内部字号不是常规像素，建议用一条 5-10 秒测试口稿做矩阵校准。

### 5. 手动文本朗读不方便

把 `caption_split` 设置为 `segment`。这样每个口稿段落对应一个文本片段，操作次数更少。
