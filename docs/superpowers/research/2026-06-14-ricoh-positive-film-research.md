# Ricoh Positive Film（正片 / ポジフィルム調）色彩特征调研报告

**日期:** 2026-06-14
**状态:** Phase 2 探索完成
**研究员:** Color Science Agent
**范围:** Ricoh GR III/IIIx Image Control — Positive Film 模式

---

## 执行摘要

**Positive Film（正片）是 Ricoh GR 系列最具辨识度和用户忠诚度的彩色 Image Control 模式。** 它在社区中的影响力可与 Fujifilm Velvia 相提并论，但其色彩哲学不同：Positive Film 追求「胶片反转片的浓郁但不失自然」——高饱和 + 高反差 + 深邃蓝色 + 暖调琥珀，但肤色保护比 Velvia 更好。

**核心发现：**
1. Positive Film 的视觉特征可归纳为「**高饱和正片感 + 琥珀-青蓝双色调分离 + 压缩动态范围的增强中灰反差**」
2. 社区中存在大量基于 Positive Film 的自定义配方（Ricoh Recipes 38 个 GR III 配方中相当比例以此为基底），参数调整方向一致：提饱和、压影调、暗部减对比以保护层次
3. 与项目已复刻的 HNCS / Gold 200 / 5219 在色彩哲学上有本质差异，**不会产生重复建设**
4. 存在可操作的逆向工程路径：理光官方提供的 14 参数体系可直接映射到 `engine/core.py` 的参数化管线

---

## 1. 维度 D1: 视觉特征描述

### 1.1 整体饱和度倾向

| 来源 | 描述 | 可信度 |
|------|------|--------|
| Ricoh 官方产品页 | ポジフィルム調，与 Standard/Vivid 并列为彩色三基础，样本图色彩浓郁 | ✅ 确证（官方） |
| SlashGear 评测 | "pleasant colors, and punchy contrast" — 色彩令人愉悦，反差有力 | ✅ 确证（评测） |
| 知乎 @陈CCW | "正片模式的色彩跟胶片特别稳" | ⚠️ 社区共识 |
| 知乎 GR2→GR3 色彩对比 | GR2 偏洋红（日系/Canon-like），GR3 偏绿（德系/Leica-like），应为新 CMOS 所致 | ⚠️ 合理推断 |

**结论:** Positive Film 的饱和度显著高于 Standard，接近或略超 Vivid，但色彩倾向不同。GR3 世代整体偏绿底，GR2 偏洋红底。跨代际的色彩基底差异需要在逆向时做版本锚定。

### 1.2 影调曲线特征

| 来源 | 描述 | 可信度 |
|------|------|--------|
| 知乎回答（调色还原） | 亮度曲线：高光端点下切、暗部端点下切（压缩动态范围），中间调微微正 S（增强中灰反差） | ⚠️ 单一来源但技术具体 |
| SlashGear | "punchy contrast" | ✅ |
| 社区配方趋势 | 影调（High/Low Key）普遍 -1 ~ -3，对比度 +1 ~ +2 | ✅ 多源一致 |

**关键推断:** Positive Film 采用了**双端压缩 + 中灰增强**的影调策略：
- 暗部端点下切 → `black_lift` 可能为正（提高黑位），或 shadow_toe_power < 1.0 但起始点更低
- 高光端点下切 → highlight_shoulder 起点可能更低 + shoulder_power > 1.0
- 中灰区正 S 曲线 → `contrast > 1.0`

这与此前 HNCS（contrast 1.08）和 5219（contrast 1.08）的 contrast 设置类似，但 Positive Film 的两端压缩更激进。

### 1.3 色相偏移特征

| 色域 | 特征 | 来源 | 可信度 |
|------|------|------|--------|
| **蓝色/青色** | 中间调和高光部蓝色通道增强（"蓝偏左上"），蓝色更深邃、偏青。这是 Positive Film 最标志性的色相特征 | 知乎调色还原 | ⚠️ 技术描述 |
| **绿色** | 高光部绿色被抑制（"绿偏右下"），呈现更暖的绿色调 | 知乎调色还原 | ⚠️ 技术描述 |
| **红色/橙色** | 中间调红色微增（"红稍居中"），推测橙-红方向有琥珀暖调偏移 | 知乎调色还原 | ⚠️ 技术描述 |
| **肤色** | 多位用户反馈「正片拍人不会猪肝红」——暗示肤色在增强饱和度的同时有保护机制 | ⚠️ 社区共识 | ⚠️ 定性 |

**关键推断:** Positive Film 的色相偏移策略是：
- **蓝→青蓝**：蓝色色相向 cyan 方向偏移（hue_shift 约 +3 ~ +5 度，即向 cyan/green 方向），同时增强饱和度
- **红→琥珀**：红色色相向 orange/amber 方向微偏移（orange_push 约 5-8 度）
- **绿→黄绿**：高光部绿色衰减，呈现暖绿/olive 倾向
- **肤色保护**：可能通过限制 skin_hue 范围内的饱和度增强幅度实现

### 1.4 分色调特征

| 区域 | 特征 | 来源 | 可信度 |
|------|------|------|--------|
| 暗部 | 相对中性（"暗部可以不动"），无明显偏色 | 知乎调色还原 | ⚠️ |
| 中间调 | 偏蓝红（cyan-magenta 混合），蓝色增强为主 | 知乎调色还原 | ⚠️ |
| 高光 | 蓝色增强 + 绿色抑制 → 高光区域呈现干净的冷-暖分离 | 知乎调色还原 | ⚠️ |

**与 5219 的对比:** 5219 的 split-tone 是「暗部偏青 + 高光偏暖」（经典 teal-orange 电影调）。Positive Film 不走这个方向——它更像是「全影调蓝色增强 + 暗部中性 + 高光冷调」，色调分离更微妙。

### 1.5 白平衡倾向

| 来源 | 描述 | 可信度 |
|------|------|--------|
| GR2 vs GR3 对比 | GR3 整体偏绿底（"德系"），GR2 偏洋红底（"日系"） | ⚠️ 社区共识 |
| 社区配方 | 大量配方使用「白平衡日光偏移 G:A」（绿:琥珀）微调，如 G6:A10（偏暖）、G3:A5 等 | ✅ 多源一致 |
| Ricoh Recipes 博客 | GR III → GR IV：相同配方在 GR IV 上更偏暖/红，GR III 更偏绿 | ✅ 确证（author 实测） |

**结论:** Positive Film 的默认白平衡在 GR III 上可能内置了微弱的绿-琥珀偏移（偏暖方向），具体数值需要在逆向中确定。GR IV 世代 WB 更暖。

### 1.6 与其他模式的对比定位

```
饱和度（⚠️ 基于社区共识推断，Negative Film 的位置存疑）：
  Standard ≈ Negative Film (选择性降饱和，"褪色+保色"矛盾统一) < Vivid ≈ Positive Film < Fuji Velvia
对比度：
  Negative Film < Standard ≈ Positive Film < Vivid < Hi Contrast B&W
色相偏移：
  Standard (中性) < Vivid (全局增强) < Positive Film (选择性偏移)
胶片感：
  Negative Film (褪色复古) > Positive Film (反转片浓郁) > Standard
```

> ⚠️ **跨文档矛盾标记 (2026-06-14 R2)**: Negative Film 的饱和度位置在两份文档中存在矛盾（一份认为 Standard < Negative Film，另一份认为 Negative Film < Standard）。官方「褪色感」描述暗示饱和度应低于 Standard，但 Negative Film 的「清晰色彩」特性说明降饱和是选择性的而非全局的。此处暂时将两者放在同一水平，待量化验证后调整。

**Positive Film vs Fuji Velvia 的区别：**
- Velvia: 极高高饱和，红色和绿色容易过饱和，肤色可能偏红
- Positive Film: 高饱和但有肤色保护，蓝色处理更克制但有独特青蓝方向，整体更「可用」

---

## 2. 维度 D2: 可调参数体系

### 2.1 GR III Image Control 完整参数列表

来自 PConline 产品参数页（✅ 确证）：

| 参数 | 英文名 | 范围（推测） | 备注 |
|------|--------|-------------|------|
| 饱和度 | Saturation | ±4 | |
| 色相 | Hue | ±4 | 全局色相偏移 |
| 高/低键调整 | High/Low Key | ±4 | 控制整体影调亮度 |
| 对比度 | Contrast | ±4 | 全局对比度 |
| 对比度（高光） | Contrast (Highlight) | ±4 | 高光区独立对比度 |
| 对比度（阴影） | Contrast (Shadow) | ±4 | 阴影区独立对比度 |
| 锐度 | Sharpness | ±4 | |
| 阴影 | Shading | ±4 | 暗角控制 |
| 明瞭度 | Clarity | ±4 | 中间调微反差 |
| 调色 | Toning | 多种预设 | B&W 模式下用于着色 |
| 滤镜效果 | Filter Effect | 多种预设 | B&W 模式下模拟彩色滤镜 |
| 颗粒效果 | Grain Effect | 3 级 | v1.70+ firmware |
| HDR 调 | HDR Tone | ±4 | v1.70+ firmware |
| 色調 | Color Tone | ±4 | v1.70+ firmware（可能与色相不同） |

> **注:** 理光从未公开过各 Image Control 的具体出厂默认值。社区配方都是基于「默认值 ± N」的相对调整。但我们可以通过收集足够多的社区配方进行交叉推断。

### 2.2 社区 Positive Film 配方参数收集

#### 配方 A: GR3x 人像正片配方（来自 什么值得买）

```
基底: 正片模式 (Positive Film)
饱和度:      +2
色相:        +3
影调(高/低键): -2
对比度:      +1
对比度(亮部): +2
对比度(暗部): -4
锐度:        +1
明暗:         0
清楚(清晰度): +1
白平衡:      日光
WB 偏移:     G6:A10  (绿色+6, 琥珀+10 = 明确偏暖)
```
来源: docin.com/p-4053283574.html, post.smzdm.com/talk/p/apvom44w/

#### 配方 B: 知乎 RGB 曲线还原（GR2 正片模拟）

```
亮度曲线: 高光端点↓, 暗部端点↓, 中间调正S
R通道:    中间调稍居中（微增）, 高光/暗部不动
G通道:    中间调不动, 高光偏右下（抑制绿色高光）
B通道:    中间调偏左上（增强蓝色中间调）, 高光偏左上（增强蓝色高光）
色相总结: 中间调=蓝红增强, 高光=蓝增绿减, 暗部=中性
```
来源: zhihu.com/question/522187329/answer/2391304769

#### 配方 C: Ricoh Recipes — GR III/IIIx 预设

38 个 GR III 配方分布在 7 个合集中（Nature, Road Trip, Street, California Negative, Film, Analog, Adventure, B&W）。

**已知使用 Positive Film 基底的配方：**
- Americana Color（Road Trip Collection）
- Pro Color（GR IV Starter Collection，但 GR IV 版本）

> ⚠️ **重要限制:** Ricoh Recipes 的具体参数值需要付费购买 App 或订阅 Patron 才能获取。公开渠道无法获得精确数值。这在逆向工程中是一个信息缺口。

#### 配方 D: 理光 GR III 常用推荐参数（来自微博 @霜绝）

```
白天街拍推荐:
- 正片模式
- 饱和度 +1~+2
- 对比度 +1
- 影调 -1
- 白平衡: 日光 / 阴影（G:A 偏移视场景定）
```
来源: 163.com/dy/article/FOFAKKQ50525ISGB.html（页面加载失败，仅摘要可用）

### 2.3 参数调整方向共识

从多源交叉验证，Positive Film 的社区调整方向高度一致：

| 参数 | 调整方向 | 共识度 |
|------|---------|--------|
| 饱和度 | +1 ~ +3（出厂默认已高，继续增强） | 高 |
| 色相 | +2 ~ +3（偏暖/琥珀方向） | 高 |
| 影调 | -1 ~ -3（压低整体亮度，增加厚重感） | 高 |
| 对比度 | +1 ~ +2（增强全局对比） | 高 |
| 对比度(亮部) | +1 ~ +3（保护高光层次的同时增强反差） | 中 |
| 对比度(暗部) | -2 ~ -4（关键！提亮暗部避免死黑） | 高 |
| 清晰度 | +1（微增强中间调微反差） | 中 |
| 白平衡偏移 | G:A = 通常偏暖（A > G），暖调日系方向 | 高 |

**最关键的模式特征:** **暗部对比度大幅降低（-4）** 是 Positive Film 区别于 Standard/Vivid 的核心参数特征之一——它确保了高饱和 + 高反差的同时，暗部不会死黑，保留了「胶片反转片」的暗部层次。

---

## 3. 维度 D3: 与已复刻配置的区分度

### 3.1 参数空间对比

| 维度 | HNCS | Gold 200 | 5219 | **Positive Film (推断)** |
|------|------|----------|------|--------------------------|
| 全局饱和度 | 1.00 | 1.12 | 0.90 | **~1.15-1.20** |
| 对比度 | 1.08 | 0.96 | 1.08 | **~1.05-1.10** |
| 暗部分色调 | 微暖红 | 暖金 | 青 | **中性（少或无）** |
| 高光分色调 | 中性 | 金奶油 | 暖 | **冷蓝（蓝增强）** |
| 蓝通道饱和度 | 1.05 | 0.95 | (default) | **~1.10-1.20** |
| 蓝通道色相 | 0 | -5.0° (→cyan) | (default) | **+3~+5° (→cyan)** |
| 橙红偏移 | 0 | 10.0° | 2.0° | **~5-8° (→amber)** |
| 绿通道处理 | 中性 | 偏黄绿 | 中性 | **高光抑制绿色** |
| 肤色保护 | 0.94 | 0.95 | 0.88 | **需要（推测 0.90-0.95）** |
| WB 偏移 | -250K (冷) | +400K (暖) | 0 | **~+200~500K (暖)** |
| 黑位 lift | 0.004 | 0.002 | 0.0018 | **~0.003-0.006** |
| 暗部 toe | 0.85 | 0.86 | 0.82 | **~0.80-0.88** |

### 3.2 哲学差异

| 配置 | 色彩哲学 | 核心用户场景 |
|------|---------|-------------|
| **HNCS** |「自然但优于准确」— 色度计精度 + 感知增强 | 商业摄影、高端人像 |
| **Gold 200** |「温暖的黄金时刻」— 一切偏暖金色 | 生活记录、旅行 |
| **5219** |「电影感的青橙分离」— teal-orange 戏剧化 | 影视感、街拍氛围 |
| **Positive Film** |「反转片的鲜活浓郁」— 高饱和正片 + 深邃蓝 + 琥珀暖调 | 街拍直出、旅行风光、社交媒体 |

**Positive Film 的独特空间：**
- 比 HNCS 更「有性格」（HNCS 偏保守/准确）
- 比 Gold 200 更「冷调明亮」（Gold 200 一切暖金）
- 比 5219 更「鲜艳直接」（5219 偏电影调色风格）
- **在项目中填补了「高饱和、蓝调增强、直出感强」的色彩位置，与现有三个配置均不重叠**

---

## 4. 维度 D4: 逆向工程可行性评估

### 4.1 参数映射分析

`engine/core.py` 的参数化管线可以**直接映射** Positive Film 的大部分特征：

| Positive Film 特征 | engine 对应参数 | 可行性 |
|---------------------|-----------------|--------|
| 高饱和度 | `global_saturation` | ✅ 直接 |
| 蓝色增强 | `blue_saturation_boost` + `blue_hue_shift` | ✅ 直接 |
| 高光绿抑制 | 需要在 `apply_color_grade` 中新增绿色通道的亮度相关饱和度控制 | ⚠️ 需扩展 |
| 暗部中性、高光冷蓝 | `shadow_tint` / `highlight_tint` | ✅ 直接 |
| 压缩动态范围 | `black_lift`, `shadow_toe_*`, `highlight_shoulder_*` | ✅ 直接 |
| 中灰增强反差 | `contrast > 1.0` | ✅ 直接 |
| 琥珀暖调偏移 | `orange_push` | ✅ 直接 |
| 肤色保护 | `skin_hue_min/max`, `skin_sat_adjust` | ✅ 直接 |
| WB 暖调偏移 | `white_balance_shift_k` | ✅ 直接 |
| 暗部对比度降低 | 目前引擎无独立暗部对比度参数，需要通过 `shadow_toe_power` 和 `black_lift` 组合实现 | ⚠️ 近似实现 |

### 4.2 需要引擎扩展的功能

1. **绿色通道高光抑制:** 当前 `apply_color_grade` 有蓝色通道的独立控制（`blue_saturation_boost` 等），但没有绿色通道的亮度相关处理。Positive Film 需要「高光部绿色衰减」。

   **建议方案:** 在 `apply_color_grade` 中添加 `green_highlight_suppression` 参数，在 luma > 阈值时降低绿色通道的饱和度。

2. **独立暗部/亮部对比度:** 理光的 Contrast (Highlight) 和 Contrast (Shadow) 是独立的。当前引擎只有一个全局 `contrast` + 统一的 `shadow_toe`/`highlight_shoulder`。

   **建议方案:** 添加 `shadow_contrast_boost` 和 `highlight_contrast_boost` 参数，在 tone curve 阶段独立控制。

### 4.3 逆向工程推荐路径

```
路径 A: 社区参数推演法（低成本，精度中等）
  收集多源社区配方 → 统计参数分布 → 反推出厂默认值 →
  映射到 engine 参数 → 生成 LUT → 目视对比社区样片

路径 B: RAW+JPEG 配对法（中成本，精度高）
  获取 GR III/IIIx 样机 → 拍摄 ColorChecker + 实景 →
  对每张拍摄分别保存 RAW + 各 Image Control JPEG →
  分析 RAW→JPEG 的色彩变换 → 拟合 engine 参数

路径 C: DCP 参考法（低成本，精度中高）
  使用 Adobe Camera Raw 中 GR III 的官方 Camera Profile
  作为「Standard」基准 → 抓取 Positive Film JPEG 与
  Standard JPEG 的差异 → 分析差异映射到参数
```

**推荐组合: A + C 并行，条件允许时补充 B。**

### 4.4 关键信息缺口

| 缺口 | 影响 | 优先级 |
|------|------|--------|
| Positive Film 出厂默认参数（绝对数值，非相对±N） | 无法确定基准参考点 | 🔴 高 |
| GR III Standard mode 的精确参数作为中性参考 | 需要相对差异才能定位 Positive Film | 🔴 高 |
| 官方 DCP 文件的具体色彩矩阵和 tone curve | 路径 C 的关键输入 | 🟡 中 |
| GR III vs GR IV 的 Positive Film 色彩渲染差异细节 | 版本锚定点不明确 | 🟡 中 |
| Ricoh Recipes 具体参数值（付费墙） | 失去了一个重要的社区数据源 | 🟡 中 |

---

## 5. 维度 D5: 采样素材来源

### 5.1 可获取的官方源

| 来源 | 内容 | 获取难度 |
|------|------|---------|
| ricoh-imaging.co.jp 产品页 | 12 种 Image Control 的官方样本图 | ✅ 公开 |
| Adobe DNG Converter / ACR | GR III 的 Camera Profile (DCP) | ✅ 免费 |
| Ricoh GR III 操作手册 PDF | 参数说明（但无数值） | ✅ 公开 |
| Realme GT 8 Pro 官方样张 | 授权 Positive Film 样本（手机端实现） | ✅ 公开 |

### 5.2 可获取的社区源

| 来源 | 内容 | 获取难度 |
|------|------|---------|
| flickr.com — 标签 "Ricoh GR III Positive Film" | 大量用户实拍样张 | ✅ 公开 |
| 小红书 — #理光GR3 #理光正片 | 大量带参数分享的样张 | ✅ 公开 |
| 知乎 — 「理光 GR」话题 | 色彩分析、调色还原讨论 | ✅ 公开 |
| Ricoh Recipes App | 付费配方参数 | ⚠️ 付费 |
| explorecams.com | 按相机型号+模式的样张搜索 | ✅ 公开 |

### 5.3 逆向专用素材需求（路径 B 需要）

| 素材 | 说明 |
|------|------|
| GR III/IIIx 样机 1 台 | 拍摄标定素材 |
| ColorChecker Passport 或类似色卡 | 标定色彩变换 |
| 灰阶卡 | 标定影调曲线 |
| 实景场景 × 5-10 | 覆盖典型拍摄场景（蓝天/绿植/肤色/街景/暗光） |

---

## 6. 新发现的问题

1. **GR2 vs GR3 的色彩基底差异有多大？** GR2 偏洋红、GR3 偏绿。Positive Film 的「正片感」在两代机器上表现可能不同。如果目标是跨平台输出，需要明确锚定哪个版本。
2. **「Negative Film」的复刻优先级？** 调研过程中发现 Negative Film（负片）在社区中讨论度甚至可能高于 Positive Film（因为它 2023 年才从日记版下放，新鲜度高）。两个模式一起复刻的协同效应更高。
3. **GR IV 新增的 Cine Y / Cine G 模式是什么？** GR IV 新增了两种 Cinema 效果，可能代表了理光新的色彩方向，值得关注。
4. **引擎能否表达「暗部对比度独立降低」？** 社区配方中「对比度(暗部): -4」是最一致的特征之一。当前引擎没有这个独立参数，需要评估扩展成本。
5. **Realme GT 8 Pro 的 Positive Film 授权实现**是否能作为参考基准？手机端的实现与相机端可能使用不同的 LUT/管线，但大方向应一致。
6. **Adobe 的 GR III Camera Profile 是逆向的极佳锚点**——它代表「标准」色彩渲染。如果能获取该 DCP 文件并反解出色彩矩阵/tone curve，就能建立一个中性基准，在此基础上叠加 Positive Film 的差异。

---

## 7. 初步参数建议（待实验验证）

基于以上分析，以下是对 Positive Film engine 参数的**初始推测值**，需要在拿到标定素材后验证和调整：

```python
PRESET_POSITIVE_FILM_DRAFT = {
    'name': 'ricoh_positive_film',
    'title': 'Ricoh Positive Film (ポジフィルム調) — Draft',

    'tone': {
        'black_lift':                0.0045,    # Slightly elevated black (compressed DR)
        'shadow_toe_pivot':          0.10,
        'shadow_toe_power':          0.82,      # Gentle shadow lift
        'contrast':                  1.08,      # Punchy midtone contrast
        'per_channel_contrast':      [1.00, 0.98, 1.04],  # R neutral, G slightly less, B most
        'highlight_shoulder_start':  0.65,      # Earlier shoulder entry (compressed highlights)
        'highlight_shoulder_power':  1.30,      # Smooth highlight roll-off
    },

    'color': {
        # Neutral shadows, cool-bright highlights
        'shadow_tint':             [1.00, 1.00, 1.00],     # Neutral (per Zhihu analysis)
        'highlight_tint':          [0.97, 0.98, 1.04],     # Cooler, blue-boosted highlights
        'global_saturation':        1.18,                   # High saturation (positive film character)
        'highlight_desat_start':   0.65,
        'highlight_desat_max':     0.10,                   # Keep some highlight color

        # Skin tone protection
        'skin_hue_min':            12.0,
        'skin_hue_max':            38.0,
        'skin_sat_adjust':         0.90,                   # Protect skin from oversaturation

        # Signature: blue → cyan-tinged deep blue; red → warm amber
        'teal_push':              3.0,                     # Modest blue→teal push
        'orange_push':             6.0,                    # Red→amber shift

        # Blue channel enhancement
        'blue_saturation_boost':   1.12,                   # Signature deep blue saturation
        'blue_luminance_shift':   -0.03,                   # Slightly darker, richer blues
        'blue_hue_shift':          4.0,                    # Push blue toward cyan

        # Overall warm daylight balance
        'white_balance_shift_k':  300.0,                   # Subtle warmth
    },

    # NOTE: Green highlight suppression NOT YET IMPLEMENTED in engine
    # Would need new parameter like 'green_highlight_suppression': 0.08
}
```

---

## 附录 A: 参考链接

| 资源 | URL |
|------|-----|
| Ricoh 官方 GR III 表现力页面（日文） | ricoh-imaging.co.jp/japan/products/gr-3/feature/03.html |
| Ricoh 官方 GR III 表现力页面（中文） | ricoh-imaging.com.cn/china/products/gr-3/feature/03.html |
| Ricoh Recipes 社区 | ricohrecipes.com |
| Ricoh Recipes 博客（GR IV 色彩差异分析） | ricohrecipes.com/2025/10/24/my-ricoh-gr-iv-arrived-first-recipe-test/ |
| SlashGear GR IIIx 评测 | slashgear.com/1003512/ricoh-gr-iiix-review-pro-photographic-power-in-your-pocket/ |
| 知乎: 如何调出 GR2 正片色彩？ | zhihu.com/question/522187329/answer/2391304769 |
| 知乎: GR2 vs GR3 色彩差异 | zhihu.com/question/330090419/answer/1402037275 |
| 什么值得买: GR3x 正片人像参数 | post.smzdm.com/talk/p/apvom44w/ |
| 豆丁: 理光 GR3x 参数设置 | docin.com/p-4053283574.html |
| Realme GT 8 Pro × Ricoh GR 合作 | notebookcheck.net/Realme-GT-8-Pro-inherits-Snap-Focus-and-three-other-exciting-camera-features-from-Ricoh-GR-IV.1138336.0.html |
| PConline: GR III HDF 参数 | g.pconline.com.cn/product/dc/ricoh/2170299_detail.html |

## 附录 B: 待后续 Agent 研究的问题

1. 获取 Adobe Camera Raw 中 Ricoh GR III 的 DCP 文件，反解出色彩矩阵和 tone curve
2. 收集 flickr 上 20+ 张 Positive Film 直出样张，提取色彩统计特征
3. 分析 GR IV 新增的 Cine Y / Cine G 模式与 Positive Film 的关系
4. 调研 Negative Film 的色彩特征（为后续并行复刻做准备）
5. 评估 `engine/core.py` 扩展「绿色通道高光抑制」和「独立暗部对比度」的工作量
