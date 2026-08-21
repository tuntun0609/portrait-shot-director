# 提示词配方

## 组装方式

查看原图后填写以下变量，不要在最终提示词中留下方括号：

- `[CROP_AND_FRAMING]`：画幅、裁切和人物位置。
- `[HEAD_DIRECTION]`：头部偏航、俯仰和侧倾。
- `[BODY_POSE]`：肩线、躯干、四肢方向、重心与遮挡。
- `[HAND_NOTES]`：逐只手记录可见指数、指序、弯曲、接触点和遮挡。
- `[FOOT_NOTES]`：逐只脚记录朝向、透视缩短、落点和遮挡。
- `[ONE_SPECIFIC_ERROR_TO_FIX]`：仅在修复时填写一个最严重的错误。

按“基础白模提示词 → 需要的风格片段”组装一份最终提示词。不要补画隐藏手指。

## 基础白模提示词

```text
Use case: style-transfer
Input images: Image 1 is the ONLY exact pose, anatomy, framing, crop, perspective, hand geometry and occlusion reference.
Primary request: Convert only the person in Image 1 into one clean featureless white artist-mannequin contour drawing on a perfectly pure white (#FFFFFF) background.

GEOMETRY — highest priority: preserve [CROP_AND_FRAMING], [HEAD_DIRECTION], [BODY_POSE], original body proportions, contact points, overlap order and foreshortening. Keep the natural left/right asymmetry. Do not center, mirror, straighten, frontalize, beautify or symmetrize the figure.

HANDS — highest priority: preserve [HAND_NOTES]. Keep every visible finger and thumb individually readable with the same order, curvature, spacing, bend, contact, overlap and perspective. Do not invent hidden fingers or add, remove, fuse or duplicate visible fingers.

OUTPUT: use smooth, confident, uniform thin-to-medium black contour lines. Draw a bald blank head, neutral smooth torso and complete limbs; retain only inner lines required for limb overlaps and visible finger boundaries. Preserve the source aspect ratio and crop.

REMOVE: background, props, facial features, ears, hair, fingernails, clothes, seams, folds, jewelry, skin texture, explicit anatomy, color, gray, shading, fill, hatching, text, watermark and border. Keep the head completely blank with no internal guide or construction lines.
```

## 双参考图角色片段

有姿势图和独立风格图时，用下面内容替换基础提示词的 `Input images`：

```text
Input images: Image 1 is the ONLY exact geometry, pose, crop, hands and occlusion reference. Image 2 controls ONLY contour smoothness, line weight, proportion abstraction, foot simplification and inner-line density. Never copy Image 2's pose, crop, limbs, hands or overlaps. On conflict, Image 1 geometry always wins.
```

## 修长极简人台风格片段

```text
STYLE PRESET — elongated minimalist fashion mannequin:
- Abstract the figure to 8.5–9.5 heads tall while keeping the referenced joints, gesture, balance, foreshortening and overlaps recognizable.
- Use long continuous S-curves, tapered limbs and a smooth neck–shoulder–torso–hip flow; no segmented joints, muscles, ribs, abdominal lines or explicit anatomy.
- Keep every visible finger distinct. Preserve [FOOT_NOTES], but simplify each foot to a rounded wedge or sock-like block with no toes, shoes, seams, heel detail or sole line.
- Keep only overlap, armpit, groin/leg-separation and finger-boundary inner lines. No joint circles, gray, shading, fill, texture or decorative strokes.
- Keep the bald head completely blank with no internal guide or construction lines.
```

## 单次修复提示词

只在首图触发硬性门槛时使用一次。以原始姿势图为 Image 1，复用首轮组装好的完整提示词，并在最前面加入：

```text
CORRECTION PASS: return one corrected final image, not variants. Fix only this highest-priority failure: [ONE_SPECIFIC_ERROR_TO_FIX]. Preserve every other pose, crop, proportion, contact, overlap and visible finger from Image 1. Do not use the failed output as a geometry reference.
```

例如：`restore the different forearm angles`、`separate the two fused curled fingers`或 `restore the three-quarter head angle`。
