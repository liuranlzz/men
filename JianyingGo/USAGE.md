# 使用流程

## 1. dry-run

```bash
cd JianyingGo
python create_draft.py \
  --input "../content/遥控4.0/遥控4.0内容.md" \
  --config "config.example.json" \
  --dry-run
```

检查：

```text
out/<草稿名>/manifest.json
out/<草稿名>/captions.srt
out/<草稿名>/scene_notes.md
```

## 2. 写入剪映草稿

```bash
python create_draft.py \
  --input "../content/遥控4.0/遥控4.0内容.md" \
  --config "config.example.json" \
  --draft-name "遥控4.0-字幕草稿"
```

本地测试真实草稿写入：

```bash
mkdir -p out/local_drafts
python create_draft.py \
  --input "../content/遥控4.0/遥控4.0内容.md" \
  --config "config.example.json" \
  --draft-root "out/local_drafts" \
  --draft-name "local-test" \
  --allow-replace
```

## 3. 打开剪映

在草稿列表找到 `遥控4.0-字幕草稿`。

检查：

- 字幕是否出现
- 字幕时间是否对应口稿
- 字幕大小是否合适
- 字幕位置是否适合后续画面

## 4. 手动生成 AI 配音

在剪映里：

1. 选中字幕文本
2. 点击文本朗读或 AI 配音
3. 选择会员音色
4. 生成音频
5. 微调音频和字幕时长

## 5. 调整字幕样式

修改 `config.example.json`：

```json
{
  "subtitle": {
    "size": 8.0,
    "transform_y": -0.78,
    "border_width": 45.0
  }
}
```

重新生成：

```bash
python create_draft.py \
  --input "../content/遥控4.0/遥控4.0内容.md" \
  --config "config.example.json" \
  --draft-name "遥控4.0-字幕草稿" \
  --allow-replace
```
