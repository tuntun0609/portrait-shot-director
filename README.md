# Portrait Shot Director

人像摄影相关 AI 技能集合，用于人像图片的分析、生成与后期处理。

## 安装

```bash
npx skills add tuntun0609/portrait-shot-director
```

安装某一个 skill

```bash
npx skills add tuntun0609/portrait-shot-director --skill analyze-portrait-prompt
```

## 技能列表

### 1. analyze-portrait-prompt
从人像参考图中提取构图、人物、姿态、服装、场景、光线等维度的提示词，并按固定顺序拼接为完整提示词。用于人像看图反推提示词、复现参考图或提取指定维度。

### 2. depth-preserving-portrait-blur
将人物图片转为近白远黑灰度相对深度条件图，弱化五官与纹理，保留人物、发型、场景轮廓和前后层次。输出 8 位 RGB PNG，适用于深度控制生图。

### 3. extract-image-color-palette
使用 Python、Pillow 和 NumPy 从图片中确定性提取主色、颜色占比及 RGB/HEX 值，直接输出文字色卡。支持 PNG、JPG、JPEG、WebP、HEIC、TIFF 或 GIF。

### 4. generate-pose-mannequin-lineart
将人物照片或姿势描述转换为纯黑线、纯白底的无五官白模动作轮廓稿，保留构图、透视、四肢、手部指序与遮挡关系。支持修长极简时装人台和真实比例白模。

### 5. naturalize-ai-portrait-prompt
优化写实人像生成或图片编辑提示词，减少塑料皮肤、过度完美、棚拍摆拍等 AI 痕迹，让画面更像可信的真人实拍或日常快照。

### 6. portrait-shot-director
为人像图像生成与编辑任务提供统一入口，按需组织工具、执行流程和视觉参考。不可以单独使用

