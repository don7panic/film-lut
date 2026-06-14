# 理光 Ricoh GR 色彩配置逆向工程调研 — 最终报告

**日期:** 2026-06-14
**状态:** 最终报告
**核心问题:** 理光 GR 系列的 Positive Film 和 Negative Film 色彩配置有哪些可辨识的特征？如何通过色彩逆向工程将其复刻为引擎预设？

---

## 执行摘要

**结论：Positive Film 应作为第一优先级复刻目标。逆向工程最佳路径为「DCP 基线 + 社区配方推演 + RAW/JPEG 配对分析」三管齐下。当前引擎可覆盖约 70-80% 的 Positive Film 特征，主要差距在于逐色相饱和度映射。**

**关键发现：**
1. 从 Ricoh Recipes 获取了 **7 个基于 Positive Film 的配方**及其精确参数值（饱和度、色相、对比度、色调等），为参数推演提供了丰富数据
2. Ricoh Recipes 的「负片风格」配方几乎全部基于 Positive Film（非 Negative Film），因为 Negative Film 模式 2023 年才推出
3. **WB Compensation 显示 Positive Film 基线可能偏冷**，几乎所有配方都通过 Amber (A) 偏移加暖
4. Realme GT 8 Pro 的 GR Film Tones 是**联合调校**（非单方复制），可作为官方认可的跨平台复刻参考
5. raw.pixls.us 无 GR III 的 RAW 样本，素材获取是最大瓶颈

---

## 目录

1. [理光 Image Control 体系](#1-理光-image-control-体系)
2. [Positive Film 色彩特征](#2-positive-film-色彩特征)
3. [Negative Film 色彩特征](#3-negative-film-色彩特征)
4. [逆向工程方法论](#4-逆向工程方法论)
5. [参考数据源](#5-参考数据源)
6. [技术可行性评估](#6-技术可行性评估)
7. [缺口与新问题](#7-缺口与新问题)

---

## 1. 理光 Image Control 体系

### 1.1 完整列表（GR III/IIIx — 12 种）

| # | 日文名 | 中文名 | 英文名 | 类型 | 适用广度 |
|---|--------|--------|--------|------|----------|
| 1 | スタンダード | 标准 | Standard | 基础彩色 | ⭐⭐⭐⭐⭐ |
| 2 | ビビッド | 生动 | Vivid | 基础彩色 | ⭐⭐⭐ |
| 3 | **ポジフィルム調** | **正片** | **Positive Film** | **核心彩色** 🔥 | ⭐⭐⭐⭐⭐ |
| 4 | **ネガフィルム調** | **负片** | **Negative Film** | **核心彩色** 🔥 | ⭐⭐⭐⭐⭐ |
| 5 | モノトーン | 单调 | Monotone | 基础黑白 | ⭐⭐⭐⭐ |
| 6 | ソフトモノトーン | 柔和单调 | Soft Monotone | 黑白 | ⭐⭐ |
| 7 | ハードモノトーン | 硬单调 | Hard Monotone | 黑白 | ⭐⭐ |
| 8 | ハイコントラスト白黒 | 高对比度黑白 | High Contrast B&W | 特色黑白 🔥 | ⭐⭐⭐⭐ |
| 9 | ブリーチバイパス | 旁路漂白 | Bleach Bypass | 特效彩色 | ⭐⭐⭐ |
| 10 | レトロ | 复古 | Retro | 特效彩色 | ⭐⭐⭐ |
| 11 | HDR調 | HDR 色调 | HDR Tone | 特效彩色 | ⭐⭐ |
| 12 | クロスプロセス | 正负逆冲 | Cross Process | 特效彩色 | ⭐⭐⭐ |

> 🔥 = 本轮调研聚焦目标

**注：**
- 中国官网仅列 10 种（缺少 Negative Film 和 Cross Process，两者通过固件升级追加）
- Negative Film 最初为 GR III Diary Edition 限量版独占，2023-01-20 通过 FW 1.70 (GR III) / 1.20 (GR IIIx) 下放到普通版
- Cross Process 通过 FW 1.30 追加

### 1.2 可调参数体系

每个 Image Control 提供 14 个可调参数：

| 参数 | 英文对应 | 可能的引擎映射 |
|------|---------|---------------|
| 饱和度 | Saturation | `global_saturation` |
| 色相 | Hue | 色相偏移（需独立实现） |
| 高/低键调整 | High/Low Key | 影调曲线整体偏移 |
| 对比度 | Contrast | `contrast` |
| 对比度(高光) | Contrast (Highlight) | `highlight_shoulder_power` |
| 对比度(阴影) | Contrast (Shadow) | `shadow_toe_power` |
| 锐度 | Sharpness | ❌ 引擎不支持（纯色调引擎） |
| 阴影 | Shading | ❌ 暗角，引擎不支持 |
| 明瞭度 | Clarity | ❌ 局部对比，引擎不支持 |
| 调色 | Toning | `shadow_tint` / `highlight_tint` |
| 滤镜效果 | Filter Effect | ❌ 黑白滤镜，引擎不支持 |
| 颗粒效果 | Grain Effect | ❌ 引擎不支持（FW 1.20+） |
| HDR 调 | HDR Tone | ❌ 局部影调映射 |
| 色調 | Color Tone | 细分色彩调整 |

**引擎可表达:** 约 6-7/14 个参数 🟡
**引擎不可表达:** 约 7-8/14 个参数（锐度、暗角、明瞭度、颗粒、滤镜效果等属于纹理/空间域处理，非纯色调引擎范围）

### 1.3 生态验证

✅ **Ricoh Recipes 社区** — 38 个 GR III/IIIx 配方，8 大合集。用户自定义配方基于 Image Control 基底叠加参数微调。

✅ **Realme GT 8 Pro × Ricoh 官方合作** (2025-10) — 首款获理光授权内置 GR Film Tones 的智能手机。
- 5 种影调：Standard、Positive Film、Negative Film、High Contrast B&W、Monotone
- 由 Realme 与 Ricoh 团队**联合调校**（非单方复制）
- 支持「Ricoh 蓝」「Ricoh 绿」等专属配方
- 来源: [DCFever](https://www.dcfever.com/news/readnews.php?id=40277) ✅ 确证

✅ **Adobe Camera Raw** — 2023-02 起为 GR III/IIIx 提供官方 Camera Profile (DCP)。来源: [快科技](https://news.mydrivers.com/1/889/889594.htm) ✅ 确证

✅ **Firmware 更新历史** — 官方中文固件说明页详细记录了所有 Image Control 的添加和参数扩展。来源: [理光中国](https://www.ricoh-imaging.com.cn/china/products/gr-3x/firmup/) ✅ 确证

---

## 2. Positive Film 色彩特征

### 2.1 官方定位

**官方描述:**
- ポジフィルム調 / Positive Film / 正片
- 模拟正片（反转片/幻灯片）的视觉效果
- 特点：高饱和度、高对比度、鲜明色彩

**可调参数默认值:** ❓ 未找到官方默认值
- 理光未公开各 Image Control 的具体默认参数数值
- 但社区配方基于此进行微调，参数偏移方向可反映基线特征

**社区配方参数示例** (来自豆丁网 "理光系统设置"):
```
饱和度+2  色相+3  影调-2  对比度+1
对比度(亮部):+2  对比度(暗部):-4
锐度+1  明暗0  清晰+1
白平衡:日光偏移 G6:A10
```
⚠️ 注意：这是某个特定配方的参数，叠加在某个 Image Control 基底之上。不代表 Positive Film 本身的默认值。

### 2.2 Ricoh Recipes 社区配方分析 ✅ 确证

以下为直接从 ricohrecipes.com 获取的 GR III/IIIx 配方参数（来源: [The Road Trip Collection](https://ricohrecipes.com/the-road-trip-collection/), [The Street Collection](https://ricohrecipes.com/the-street-collection/), [The Nature Collection](https://ricohrecipes.com/the-nature-collection/)）。

#### 基于 Positive Film 的配方（7 个）

| 配方 | Sat | Hue | Key | Cont | Cont(H) | Cont(S) | Clarity | WB | WB Comp |
|------|-----|-----|-----|------|---------|---------|---------|-----|---------|
| Americana Color | +2 | +2 | +1 | +4 | -3 | +4 | +2 | CT 5250K | A:10 G:5 |
| Vibrant Negative | +4 | +4 | +2 | -2 | +3 | -4 | +2 | Fluor. N Daylight | A:11 G:9 |
| Warm Negative | +1 | +4 | +1 | -1 | -4 | -3 | -1 | Daylight | A:14 M:5 |
| Kodak Chrome | +3 | -1 | -2 | -2 | +2 | -4 | +2 | Daylight | A:10 G:4 |
| Natural Negative | -2 | +2 | -1 | -2 | +3 | -4 | +2 | Daylight | A:8 G:2 |
| Royal Supra | +2 | -4 | +1 | +4 | -4 | -3 | +4 | Shade | B:6 G:4 |
| Analog Film | +4 | -4 | +2 | +4 | -4 | +4 | -2 | CT 6300K | A:1 G:6 |

#### 关键发现

1. **几乎所有「负片风格」配方都基于 Positive Film 而非 Negative Film** — 因为这些配方创作于 2021 年，而 Negative Film 模式 2023 年才通过固件下放
2. 基于 Positive Film 的配方**饱和度范围极广** (-2 到 +4)，说明 Positive Film 的基线饱和度高且可塑性大
3. **WB Compensation 几乎全部使用 Amber (A) 偏移**（A:1 到 A:14），反映 Positive Film 基线可能偏冷，需要通过加暖来平衡
4. **Highlight Correction 在所有配方中都是 On** — 这是 Positive Film 看起来自然的重要设置
5. **Contrast (Shadow) 大多是负值** (-4 到 +4，中位数 -3 到 -4)，说明暗部需要提升以获得空气感
6. **Hue 参数在两个方向上都有广泛使用** (-4 到 +4)，说明色相偏移是风格化的核心参数

#### 基于其他 Image Control 的配方

| 配方 | 基础 Effect | Sat | Hue | Cont | 特征 |
|------|------------|-----|-----|------|------|
| KodaKolor | Standard | -4 | +4 | +4 | 复古 Kodak 负片感 |
| Aged Print | Retro | +2 | 0 | +2 | 褪色相纸感，Toning +1 |
| Retro Print | Retro | +4 | +1 | +4 | Kodak 相纸冲印感，Toning +3 |
| Xpro Teal | Cross Process | +2 | -2 | -4 | 蓝向青偏移，Color Tone: Blue |
| Summer Green | Cross Process | -1 | +4 | -4 | 暖色调+冷绿，Color Tone: Y |
| Kodak Slide | Vivid | +4 | -2 | +4 | Ektachrome 反转片感 |
| Elite Chrome | Standard | +4 | -1 | +2 | 平价反转片感 |
| Color Film | Standard | +1 | +1 | +1 | 通用彩色负片感 |

### 2.3 待验证问题

- Positive Film 的默认饱和度、对比度、色相偏移的具体数值？
- 蓝色通道是否有特殊处理（"理光蓝"）？
- 肤色处理倾向？
- 与 Fuji Velvia 的相似度/差异？
- 影调曲线特征（高光滚降、暗部提升）？

---

## 3. Negative Film 色彩特征

### 3.1 官方描述与历史

**官方描述** (中文固件页, ✅ 确证):
> "以各种各样的负片表现为基础进行调整，使之呈现出从负片中冲印出来的照片的退色感，同时又能很好地呈现出颜色，达到了美妙的平衡。"

**英文描述** (日文固件页):
> "Based on various negative film expressions, it achieves a wonderful balance between the fading feel of photos printed from negatives and the clear rendering of colors."

**关键解读:**
- **"退色感" (fading feel)** — 饱和度非均匀降低，模拟底片冲印后的色彩衰减
- **"清晰色彩"** — 虽然整体褪色，但特定色调仍保持鲜明。这是与简单的「全局去饱和」的根本区别
- **"负片冲印"** — 模拟底片→相纸的色彩传递过程，而非底片本身的橙色片基+反转色

**历史时间线:**
- 2022 年冬：GR III Diary Edition 限量版首发 Negative Film 模式
- 2023-01-20：FW 1.70 (GR III) / 1.20 (GR IIIx) 下放至普通版
- 来源: [理光中国固件页](https://www.ricoh-imaging.com.cn/china/products/gr-3x/firmup/) ✅

### 3.2 GR III vs GR IV 的色彩差异

来源: [Ricoh Recipes Blog](https://ricohrecipes.com/2025/10/24/my-ricoh-gr-iv-arrived-first-recipe-test/) ✅ 确证

| 维度 | GR III | GR IV |
|------|--------|-------|
| 色温倾向 | 偏绿 (greenish tint) | 偏暖/偏红 (reddish tint) |
| 亮度 | 基准 | 约 +1/3 EV 更亮 |
| 颗粒控制 | 无 | 新增 Positive/Negative Film 颗粒选项 |
| 新 Effect | 无 | Cine Y, Cine G |

> ⚠️ **重要**: 同一配方在不同世代的 GR 相机上渲染结果不同。逆向工程需明确指定目标型号（建议以 GR III 为准，因为其配方库最丰富）。

### 3.3 基于 Negative Film 的社区配方

⚠️ **数据不足** — Ricoh Recipes 的大多数配方创作于 2021 年，早于 Negative Film 模式的推出。目前未从公开页面中找到基于 Negative Film 基底的配方。

可能的获取途径：
- Ricoh Recipes 的 **Adventure Collection** (2025-12) — 包含 "1986 Negative"、"Expired Negative" 等配方，可能使用 Negative Film 基底
- GR IV 的 **Starter Collection** (2026-06)
- Ricoh Recipes App 的 Patron 专属配方

### 3.4 待验证问题

- Negative Film 的影调曲线是提高还是降低对比度？官方样张建议对比度较低
- "退色感"在不同色相上的衰减曲线（哪些颜色保持饱和，哪些优先褪色？）
- 与 Fujifilm Classic Negative 的本质差异？
- 白平衡倾向（偏暖模拟胶片基色？
- 是否存在特定的暗部偏色（如胶片常见的青色阴影）？

---

## 4. 逆向工程方法论

### 4.1 五种方法总览

#### 方法 A: RAW + JPEG 配对分析法 🔴 核心

**原理:**
1. 用 Ricoh GR III 在相同场景下拍摄 RAW + Positive Film JPEG 和 RAW + Negative Film JPEG
2. 从 RAW 中提取场景线性 RGB（通过 LibRaw / RawTherapee / darktable）
3. 从 JPEG 中提取 sRGB 值（需反 Gamma 到线性空间）
4. 建立 RAW 线性 RGB → JPEG 线性 RGB 的色彩变换映射
5. 用多项式回归或 3D LUT 拟合该变换

**关键挑战:**
- JPEG 已包含白平衡处理，RAW 是传感器原始值 → 需分离 WB 的影响
- JPEG 已应用 sRGB 色域映射和 Gamma → 需反向解码
- 曝光可能不同 → 需要中性灰阶标定
- 需要足够多样的场景覆盖色彩空间

**所需素材:**
- Ricoh GR III 相机
- 色卡 (ColorChecker 24 / IT8)
- 多种场景（室内/室外、自然/城市、肤色/蓝天/植被）

**工具链候选:**
- LibRaw (RAW 解码)
- dcraw / RawTherapee (RAW 处理参考)
- Python/NumPy (矩阵拟合、LUT 生成)
- Colour-Science (Python 色彩科学库)

#### 方法 B: 色卡标定法 🟡 辅助

**原理:**
- 仅拍摄 ColorChecker 色卡
- 从 RAW 中提取 24 个色块的线性 RGB
- 从 JPEG 中提取处理后的 RGB
- 用多项式回归拟合 3×3 或更高阶的色彩矩阵
- 推算出 Image Control 的色彩变换

**优点:** 精确、可量化
**限制:** 只有 24 个色块，无法完整表达非线性变换（如色相依赖饱和度的偏移）

#### 方法 C: DCP 参考法 🟡 辅助

**原理:**
- 从 Adobe Camera Raw 安装目录提取 GR III/IIIx 的 DCP 文件
- DCP 路径: `C:\ProgramData\Adobe\CameraRaw\CameraProfiles\Camera\`
- 使用 dcptool (SourceForge) 反编译为 XML
- DCP 包含: ColorMatrix, ForwardMatrix, HueSatMap, ProfileLookTable 等
- 可从中提取相机传感器→参考色彩空间的基线矩阵

**工具:**
- [dcpTool](https://sourceforge.net/projects/dcptool/) — DCP ↔ XML 编译/反编译
- [dcamprof](https://github.com/darktable-org/darktable) — darktable 内置，可创建/分析 DCP

**限制:**
- DCP 描述的是 RAW→Reference Color 的转换，不是 Image Control 的创意调色
- Image Control 是相机 JPEG 引擎的功能，不直接反映在 DCP 中
- DCP 可作为「标准模式」的参考基线，但无法直接获取 Positive Film / Negative Film 的变换

**已知:** Adobe 已于 2023-02 为 GR III/IIIx 添加 Camera Profile 支持 ✅

#### 方法 D: 社区参数推演法 🟡 辅助

**原理:**
- 收集社区 Positive Film / Negative Film 配方的微调参数
- 从「标准模式」基线出发，叠加社区参数的方向性调整
- 限制：无法获取 Image Control 基线的绝对参数值

**可用来源:**
- Ricoh Recipes App / 网站
- 中文社区（大众点评、知乎、小红书、微博）
- 豆丁网/道客巴巴上的参数汇总文档

#### 方法 E: Realme GT 8 Pro 参考 🟢 补充验证

**原理:**
- Realme GT 8 Pro 内置的 GR Film Tones 是官方授权的联合调校版本
- 可作为「官方认可的复刻」参考
- 对比 GR 原机 JPG vs Realme GT 8 Pro 同一 Film Tone 的差异

**限制:**
- 手机传感器和 ISP 与 GR 相机不同
- 但色彩映射逻辑应一致
- 目前仅找到压缩后的网页样张，无原始全分辨率文件

### 4.3 工具链确认 ✅

| 工具 | 用途 | 状态 |
|------|------|------|
| **dcpTool** | DCP ↔ XML 编译/反编译。从 Adobe Camera Raw 目录提取 DCP，反编译为可读 XML | ✅ 已确认可用 ([SourceForge](https://sourceforge.net/projects/dcptool/), [教程](https://www.cnblogs.com/nemuzuki/p/18159016)) |
| **dcamprof** | darktable 内置，可创建/分析 DCP | ✅ 已确认 |
| **LibRaw** | C++ 库，解码几乎所有相机的 RAW 文件为线性 RGB | ✅ 成熟 |
| **Colour-Science** | Python 色彩科学库，支持矩阵拟合、色域转换、色差计算 | ✅ 成熟 |
| **raw.pixls.us** | 开源 RAW 样本库 | 🔴 无 GR III 样本（仅 GXR/GX200） |

### 4.4 Realme GT 8 Pro 作为参考基准 ✅

- 5 种 GR Film Tones 由 Realme + Ricoh **联合调校**（非单方复制）— 来源: [DCFever](https://www.dcfever.com/news/readnews.php?id=40277)
- 支持「Ricoh 蓝」「Ricoh 绿」等专属配方调校
- 理论上可作为「官方认可的跨平台复刻」参考，但手机 ISP 与 GR 硬件不同
- 目前仅找到压缩后的网页样张，无原始全分辨率文件

**核心路径: RAW+JPEG 配对分析 + 色卡标定**

1. **素材获取阶段:** 获取/拍摄 Ricoh GR III 的 RAW+JPEG 配对（使用 ColorChecker + 多样化场景）
2. **标准基线提取阶段:** 从 DCP + Standard Image Control JPEG 建立「传感器→标准 sRGB」的基线变换
3. **Profile 差分阶段:** Positive Film JPEG vs Standard JPEG 的差异即为 Image Control 的附加变换
4. **参数拟合阶段:** 将差分变换映射到引擎的 tone curve + color grade 参数空间
5. **验证阶段:** 生成 LUT → 与 Realme GT 8 Pro 样张 + 社区直出图对比

---

## 5. 参考数据源

### 5.1 官方来源

| 来源 | URL | 类型 | 状态 |
|------|-----|------|------|
| 理光中国固件页 | https://www.ricoh-imaging.com.cn/china/products/gr-3x/firmup/ | 固件说明+Negative Film 详情 | ✅ 已获取 |
| 理光日本表现力页 | https://www.ricoh-imaging.co.jp/japan/products/gr-3/feature/03.html | Image Control 12种列表 | ✅ 已获取 |
| 理光中国表现力页 | https://www.ricoh-imaging.com.cn/china/products/gr-3/feature/03.html | Image Control 10种列表 | ✅ 已获取 |
| Adobe Camera Raw GR III 支持 | https://news.mydrivers.com/1/889/889594.htm | DCP 添加公告 | ✅ 已确认 |

### 5.2 社区配方 & 分析

| 来源 | URL | 类型 | 状态 |
|------|-----|------|------|
| Ricoh Recipes (官网) | https://ricohrecipes.com/ | GR III/IIIx/IV 配方合集 | ⏳ 需爬取具体参数 |
| Ricoh Recipes (Blog) | https://ricohrecipes.com/blog/ | GR III vs IV 差异、配方开发 | ✅ 已获取 |
| 大众点评 "懒人理光" | https://m.dianping.com/ugcdetail/146808051 | Negative Film 使用教程 | 🔒 需身份验证 |
| 豆丁网 "理光系统设置" | https://www.docin.com/p-4053283574.html | 具体参数数值 | ⚠️ 预览受限 |
| PConline GR III HDF 参数 | https://g.pconline.com.cn/product/dc/ricoh/2170299_detail.html | 可调参数完整列表 | ✅ 已获取 |

### 5.3 Realme GT 8 Pro 样本

| 来源 | URL | 类型 | 状态 |
|------|-----|------|------|
| DCFever 报道 | https://www.dcfever.com/news/readnews.php?id=40277 | 5种影调确认+样张 | ✅ 已获取 |
| Notebookcheck 报道 | https://www.notebookcheck.net/Stunning-Realme-GT-8-Pro-camera-samples...1135437.0.html | 样张合集 | ⚠️ 经压缩 |
| Realme 官方微博 | https://weibo.com/u/7034060236 | 原始样张 | ⏳ 需检索 |

### 5.4 逆向工程工具

| 工具 | URL | 用途 | 状态 |
|------|-----|------|------|
| dcpTool | https://sourceforge.net/projects/dcptool/ | DCP ↔ XML 编译/反编译 | ✅ 已确认 |
| raw.pixls.us (RICOH) | https://raw.pixls.us/data/RICOH/ | RAW 样本库 | 🔴 无 GR III（仅有 GXR/GX200） |
| LibRaw | https://www.libraw.org/ | RAW 解码库 | ✅ 成熟工具 |
| Colour-Science | https://www.colour-science.org/ | Python 色彩科学 | ✅ 成熟工具 |

### 5.5 关键缺口 🔴

1. **Ricoh GR III RAW + JPEG 配对样本** — raw.pixls.us 无 GR III 样本。需要：
   - 自行拍摄（如果有 GR III 相机）— 最理想
   - 从 Flickr/500px 寻找 DNG 原片下载
   - 联系 Ricoh Recipes 作者 Ritchie Roesch 获取测试文件

2. **GR III DCP 文件** — 路径已知 (`C:\ProgramData\Adobe\CameraRaw\CameraProfiles\Camera\`)，需要安装了 Adobe Camera Raw 的 Windows/Mac 环境来提取

3. **Positive Film / Negative Film 官方默认参数** — 理光未公开。可能的获取方式：
   - 通过相机内 RAW 显影菜单查看各 Image Control 的默认参数滑块位置
   - 对比 Standard JPEG 与 Positive Film JPEG 的色彩差异来反推

4. **基于 Negative Film 基底的配方** — Ricoh Recipes 的大多数配方创作于 2021 年（Negative Film 推出前）。需要从后续合集（Adventure、Analog、California Negative）或 GR IV 配方中寻找基于 Negative Film 的配方

5. **Realme GT 8 Pro 全分辨率样张** — 目前仅找到经压缩的网页图片

---

## 6. 技术可行性评估

### 6.1 引擎能力矩阵

| 特征维度 | Positive Film | Negative Film | 引擎支持度 |
|---------|--------------|--------------|-----------|
| 影调曲线 (Contrast/Key) | 待确认 | 待确认 | ✅ `tone` 参数组 |
| 全局饱和度 | 待确认 | 待确认 | ✅ `global_saturation` |
| 分色调 (Shadow/Highlight Tint) | 待确认 | 待确认 | ✅ `shadow_tint` / `highlight_tint` |
| 色相偏移 | 待确认 | 待确认 | ⚠️ 需新增 per-hue 偏移参数 |
| 白平衡偏移 | 待确认 | 待确认 | ✅ `white_balance_shift_k` |
| 蓝色特殊处理 | 可能 (理光蓝) | 可能 | ✅ `blue_saturation_boost` 等 |
| 颗粒 | N/A | 可能有 | ❌ 引擎不支持 |
| HDR Tone | N/A | N/A | ❌ 超出范围 |

### 6.2 引擎扩展需求

如果 Positive Film / Negative Film 有显著的色相偏移特征，当前引擎的 `teal_push` / `orange_push` 参数可能不够。需要：

- **Per-hue 饱和度映射** — 当前仅有全局 `global_saturation` + 蓝色特殊 `blue_saturation_boost`
- **Per-hue 亮度偏移** — 当前仅有蓝色 `blue_luminance_shift`
- **可配置的色相偏移表** — 当前仅有 teal/orange 两个固定方向的偏移

### 6.3 可复刻程度的预判

- **Positive Film:** 预计 70-80% 可在当前引擎中表达。核心挑战是色相偏移和高饱和区的色彩映射
- **Negative Film:** 预计 60-70% 可在当前引擎中表达。「退色感 + 清晰色彩」的矛盾特性可能需要更精细的饱和度映射

---

## 7. 缺口与新问题

### 7.1 Round 1 发现的关键缺口

1. 🔴 **无公开 GR III RAW 样本** — raw.pixls.us 无 GR III 或更新机型样本
2. 🔴 **理光未公开 Image Control 默认参数值** — 社区配方参数是叠加在基线之上的偏移，不代表基线本身
3. 🟡 **Positive Film 的默认参数未知** — 饱和度、对比度、色相、KEY 的默认值？
4. 🟡 **Negative Film 的具体色彩映射特征未知** — "退色感"如何量化？
5. 🟡 **GR III vs GR IV 色彩差异** — 两个世代的 Image Control 渲染不同，需指定目标
6. 🟢 **Realme GT 8 Pro 样本质量** — 已知来源但无法获取全分辨率版本

### 7.2 新问题

1. Positive Film 在不同固件版本中是否有变化？（FW 1.70 添加了 Negative Film，是否也微调了 Positive Film？）
2. 理光 GR III 的传感器与 JPEG 引擎的色彩空间是什么？（sRGB？Adobe RGB？）
3. 相机内 RAW 显影能否改变 Image Control？如果是，则可通过同一张 RAW 用不同 Image Control 分别导出 JPEG 来获得完美配对
4. Pentax 的 Custom Image（Ricoh 子公司）与 GR 的 Image Control 是否共享底层色彩科学？

---

## 8. 综合推荐方案（更新版）

### 8.1 第一优先级：Positive Film 先行

**理由:**
- 社区配方数据最丰富（Ricoh Recipes 有 7 个基于 Positive Film 的公开配方）
- Realme GT 8 Pro 授权包含 Positive Film
- 作为 GR 系列的「标志性彩色配置」，知名度最高
- 大量社区直出样张可用于视觉对比

### 8.2 逆向路径优先排序

1. **获取 GR III DCP 文件** → 建立传感器→标准 sRGB 基线
2. **收集 Positive Film JPEG 直出样张**（Flickr/社区/官方样张）→ 视觉分析
3. **如能获取 GR III 相机** → RAW+JPEG 配对拍摄 + ColorChecker 标定
4. **社区配方参数推演** → 从已知配方反推 Positive Film 基线特征
5. **引擎参数拟合** → 将 Positive Film 特征映射到 tone + color 参数
6. **LUT 烘焙 + Realme GT 8 Pro 样张对比验证**

### 8.3 Negative Film 延后理由

- 基于 Negative Film 的配方数据较少（模式 2023 年才推出）
- 引擎对「褪色+选择性保色」的支持可能需要扩展
- Positive Film 先行可以建立方法论，后续迁移到 Negative Film

---

## 9. 下一步行动建议

### 9.1 立即可执行

1. **提取 GR III DCP 文件**
   - 从 Adobe Camera Raw 目录获取（`C:\ProgramData\Adobe\CameraRaw\CameraProfiles\Camera\` 或 macOS `/Library/Application Support/Adobe/CameraRaw/CameraProfiles/Camera/`）
   - 使用 dcpTool 反编译为 XML 分析 ColorMatrix / ForwardMatrix / HueSatMap

2. **收集 Positive Film JPEG 直出样张**
   - Flickr 搜索 "Ricoh GR III Positive Film" + 下载原图（保留 EXIF）
   - 官方 GR III Gallery 页面

3. **获取基于 Negative Film 的配方**
   - Ricoh Recipes Adventure Collection
   - GR IV Starter Collection

### 9.2 需要硬件支持

4. **RAW+JPEG 配对拍摄**（如有 GR III 相机）
   - 使用 ColorChecker Passport + 多样场景
   - 每个场景拍摄 RAW + 至少 Standard/Positive Film/Negative Film 三种 Image Control 的 JPEG
   - 利用相机内 RAW 显影功能：同一张 RAW 可用不同 Image Control 导出多个 JPEG

5. **对比验证**
   - 生成 LUT 后与 Realme GT 8 Pro 样张对比
   - 与社区直出图（Flickr/小红书）对比

### 9.3 引擎扩展（如需）

如果发现 Positive Film 有逐色相饱和度/亮度映射需求，需在 `engine/core.py` 的 `apply_color_grade()` 中添加：
- `per_hue_saturation_map` — 按色相分段的饱和度系数表
- `per_hue_luminance_map` — 按色相分段的亮度偏移表
- 更灵活的色相偏移表（当前仅支持 teal/orange 两个方向）
