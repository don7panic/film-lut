# Ricoh Negative Film 色彩逆向工程 — 调研笔记

**日期:** 2026-06-14
**状态:** Draft preset 已创建（数据极度有限）
**核心问题:** Negative Film 的「褪色+选择性保色」如何映射到引擎参数？

---

## 数据来源

| 来源 | 内容 | 可信度 |
|------|------|--------|
| 1986 Negative 配方 | Adventure Collection，唯一 Negative Film 基底配方 | ✅ 确证 |
| 理光官方描述 | "褪色感 + 清晰色彩" | ✅ 确证 |
| 理光官方样本图 | fea03_art1_12.jpg（与 PF 不同场景，无法直接对比）| ❓ 定性 |
| GR Blog | 设计意图："日常随拍" | ✅ 确证 |

---

## 参数反推（从 1986 Negative 配方）

### 饱和度基线
- 配方 Saturation: **+4** → 基线饱和度极低（约 -3 ~ -4 等效）
- 引擎映射: `global_saturation = 0.78`（Positive Film 1.18 的 66%）
- `blue_saturation_boost = 1.12` → 蓝色有效饱和度 0.78×1.12 = 0.87（仍低于 1.0，但高于其他色相）

### 对比度基线
- 配方 Contrast: **+2** → 基线低对比度
- 引擎映射: `contrast = 0.94`（<1.0 降低对比度）

### 白平衡
- 配方: CT 6700K + **B:10 G:8** → 需要强力蓝绿补偿 → 基线极暖/偏黄绿
- 引擎映射: `white_balance_shift_k = +400K`

### 暗部
- 配方 Cont(S): **-3** → 暗部已抬升
- 引擎映射: `shadow_toe_power = 0.80`（激进暗部提升）+ `black_lift = 0.0005`

---

## Negative Film vs Positive Film 对比

| 参数 | Negative Film | Positive Film |
|------|--------------|---------------|
| `global_saturation` | 0.78（褪色） | 1.18（浓郁） |
| `contrast` | 0.94（柔和） | 1.04（鲜明） |
| `shadow_toe_power` | 0.80（激进暗部提升） | 0.90（温和） |
| `white_balance_shift_k` | +400K（暖黄绿） | -200K（冷蓝） |
| `blue_saturation_boost` | 1.12（补偿褪色） | 1.00（饱和已够） |
| `orange_push` | 0.0（无） | 6.0°（琥珀暖调） |
| `teal_push` | 0.0（无） | 3.0°（青蓝偏移） |
| 设计哲学 | 褪色打印照片 | 反转片浓郁鲜活 |

---

## 缺口

1. 🔴 **仅 1 个配方** — 8 个 Positive Film 配方的统计优势不存在
2. 🔴 **无同场景对比图** — 官方样本与 PF 是不同照片
3. 🔴 **无 Adobe DCP** — 无法提取色彩矩阵
4. 🔴 **无 RAW+JPEG 配对** — 需要 GR 相机
5. 🟡 **"选择性保色"未实现** — 当前引擎无 per-hue 饱和度映射，无法精确表达「蓝绿保留、暖色褪去」

---

## 预设文件

`presets/ricoh_negative_film.py` — V-Log only (skip_standard=True)
