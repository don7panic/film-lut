# 理光 GR 色彩配置逆向工程 — 最终调研报告

**日期:** 2026-06-14
**状态:** 最终报告（Round 1 探索 + Round 2 修复）
**核心问题:** 理光 GR 系列 Positive Film 和 Negative Film 有哪些可逆向的色彩特征？可行的逆向工程路径是什么？

---

## 执行摘要

**理光 GR 系列有 12 种 Image Control（彩色 8 种 + 黑白 4 种）。Positive Film 和 Negative Film 是辨识度最高、社区使用最广的两个配置，应作为第一优先级复刻目标。**

逆向工程的最佳路径为 **RAW+JPEG 配对法（利用相机内 RAW 显影获得完美像素对齐的配对样本）+ 色卡标定 + DCP 参考 + 社区配方推演** 四管齐下。当前引擎的参数化管线可覆盖约 70-80% 的 Positive Film 特征。最大瓶颈是素材获取（需要实际持有 GR III 相机进行标定拍摄）。

**Round 2 关键修复：** Round 1 三份文档之间的 5 个跨文档矛盾已通过 Ricoh Recipes 原始数据交叉核实解决。§2.4 社区配方方向表已替换为 7 个配方完整参数的实际数据。

---

## 1. 理光 Image Control 全景

### 1.1 完整列表（GR III/IIIx — 12 种）

| # | 日文名 | 中文名 | 英文名 | 类型 | 复刻优先级 |
|---|--------|--------|--------|------|-----------|
| 1 | スタンダード | 标准 | Standard | 彩色·基准 | - |
| 2 | ビビッド | 生动 | Vivid | 彩色·增强 | - |
| 3 | **ポジフィルム調** | **正片** | **Positive Film** | **彩色·核心** 🔥 | ⭐ 第一优先级 |
| 4 | **ネガフィルム調** | **负片** | **Negative Film** | **彩色·核心** 🔥 | ⭐ 第一优先级 |
| 5 | モノトーン | 单调 | Monotone | 黑白 | - |
| 6 | ソフトモノトーン | 柔和单调 | Soft Monotone | 黑白 | - |
| 7 | ハードモノトーン | 硬单调 | Hard Monotone | 黑白 | - |
| 8 | ハイコントラスト白黒 | 高对比度黑白 | High Contrast B&W | 黑白·特色 | 待评估 |
| 9 | ブリーチバイパス | 旁路漂白 | Bleach Bypass | 彩色·特效 | 待评估 |
| 10 | レトロ | 复古 | Retro | 彩色·特效 | 待评估 |
| 11 | HDR調 | HDR 色调 | HDR Tone | 彩色·特效 | 不推荐 |
| 12 | クロスプロセス | 正负逆冲 | Cross Process | 彩色·特效 | 待评估 |

> 🔥 Positive Film 和 Negative Film 是本次调研的核心目标。

### 1.2 生态系统验证

| 验证点 | 证据 | 可信度 |
|--------|------|--------|
| Ricoh Recipes 社区 38 个 GR III 配方 | ricohrecipes.com 三个合集页面 | ✅ 确证 |
| Realme GT 8 Pro 获理光官方授权，内置 5 种 GR Film Tones | DCFever、Realme 官方微博 | ✅ 确证 |
| Adobe Camera Raw 2023-02 起为 GR III 提供 DCP | 快科技报道 | ✅ 确证 |
| Negative Film 从 Diary Edition 限量版下放至所有 GR III | 理光中国固件页 | ✅ 确证 |
| 中文社区（小红书/知乎/微博）大量色彩参数分享 | 多源一致 | ⚠️ 定性共识 |

### 1.3 可调参数体系与引擎映射

每个 Image Control 支持 14 个可调参数。引擎可表达其中约 6-7 个核心色彩参数：

| 理光参数 | 引擎映射 | 可行性 |
|---------|---------|--------|
| 饱和度 (Saturation) | `color.global_saturation` | ✅ 直接 |
| 色相 (Hue) | HSL 全局 hue shift | ⚠️ 需扩展 per-hue 偏移 |
| 高/低键调整 (High/Low Key) | 影调曲线整体偏移 | ✅ 可通过 tone 参数 |
| 对比度 (Contrast) | `tone.contrast` | ✅ 直接 |
| 对比度·高光 (Cont. Highlight) | `tone.highlight_shoulder_power` | ✅ 近似 |
| 对比度·阴影 (Cont. Shadow) | `tone.shadow_toe_power` + `black_lift` | ⚠️ 近似实现 |
| 調色 (Toning) / 色調 (Color Tone) | `color.shadow_tint` / `highlight_tint` | ✅ 直接 |
| 锐度、明瞭度、颗粒、滤镜效果等 (7-8 个) | ❌ 纹理/空间域处理，超出色调引擎范围 | ❌ 不支持 |

---

## 2. Positive Film 色彩特征

### 2.1 官方定位

模拟彩色反转片（正片）的浓郁通透质感。Realme GT 8 Pro 媒体评测描述为 "very color-intensive Positive style" ⚠️（媒体描述，非理光官方声明）。

### 2.2 色彩特征六维画像

| 维度 | 特征描述 | 可信度 |
|------|---------|--------|
| **饱和度** | 高（接近 Vivid），但色彩倾向不同。蓝色系和红色系特别浓郁 | ⚠️ 社区共识（未量化） |
| **影调曲线** | 双端压缩（暗部/高光都切）+ 中灰增强反差（正 S 曲线）。中高对比度 | ⚠️ 知乎 RGB 曲线分析推断 |
| **色相偏移** | 蓝→青蓝（标志性"理光蓝"）、红→琥珀暖调、高光绿色被抑制 | ⚠️ 知乎 RGB 曲线分析推断 |
| **分色调** | 暗部中性、中间调偏蓝、高光冷蓝（蓝增强 + 绿抑制） | ⚠️ 知乎 RGB 曲线分析推断 |
| **白平衡** | 微暖（~+300K 推断），带绿-琥珀偏移。GR3 世代整体偏绿底 | ⚠️ 多源社区共识 |
| **肤色** | "正片拍人不会猪肝红" — 高饱和下仍有肤色保护机制 | ⚠️ 社区共识（定性） |

### 2.3 Ricoh Recipes 配方参数统计（✅ 确证 — Round 2 补充）

8 个基于 Positive Film 基底的社区配方完整参数（7 个来自 Road Trip / Street / Nature Collection + 1 个来自 Adventure Collection）：

| 配方 | Sat | Hue | Key | Cont | Cont(H) | Cont(S) | Clarity | WB | WB Comp |
|------|-----|-----|-----|------|---------|---------|---------|-----|---------|
| Americana Color | +2 | +2 | +1 | +4 | -3 | +4 | +2 | CT 5250K | A:10 G:5 |
| Vibrant Negative | +4 | +4 | +2 | -2 | +3 | -4 | +2 | Fluor. N Daylight | A:11 G:9 |
| Warm Negative | +1 | +4 | +1 | -1 | -4 | -3 | -1 | Daylight | A:14 M:5 |
| Kodak Chrome | +3 | -1 | -2 | -2 | +2 | -4 | +2 | Daylight | A:10 G:4 |
| Natural Negative | -2 | +2 | -1 | -2 | +3 | -4 | +2 | Daylight | A:8 G:2 |
| Royal Supra | +2 | -4 | +1 | +4 | -4 | -3 | +4 | Shade | B:6 G:4 |
| Analog Film | +4 | -4 | +2 | +4 | -4 | +4 | -2 | CT 6300K | A:1 G:6 |
| **Kodamax** *(新增)* | +4 | -2 | 0 | +3 | 0 | -2 | +1 | Auto | A:1 G:10 |

**关键统计（基于 8 个配方）：**
- **Saturation**: -2 ~ +4，中位数 +2.5 → 社区普遍在 Positive Film 基线上进一步增强饱和度
- **Contrast**: -2 ~ +4，正负方向都有 → 无法确定基线对比度方向，取决于目标风格（负片柔和 vs 反转片鲜明）
- **Cont(Shadow)**: 6/8 为负（-2~-4），中位数 -3.5 → **暗部对比度降低是主导趋势**，RGB 曲线分析中「暗部端点下切」与此一致
- **Hue**: -4 ~ +4，正负方向都用 → 色相偏移方向取决于配方追求的暖/冷调风格
- **WB Compensation**: 7/8 配方通过 Amber (A) 偏移加暖 → **Positive Film 基线可能偏冷**

> ⚠️ 重要限制：以上是所有参数相对于 Positive Film **基线**的叠加值，不能直接作为基线的绝对参数。

### 2.4 与项目已复刻配置的区分度

| 维度 | HNCS | Gold 200 | 5219 | **Positive Film** |
|------|------|----------|------|------------------|
| 设计哲学 | 自然但优于准确 | 胶片温暖 nostalgia | 电影感戏剧化 | 反转片浓郁鲜活 |
| 饱和度倾向 | 自然中性 (1.00) | 中等+暖调 (1.12) | 中低 (0.90) | **高 (~1.15-1.20)** |
| 蓝色处理 | 自然深度（整体色准结果）| 轻微偏暖 (0.95) | 默认 | **深度增强偏青 (1.10-1.20)** |
| 白平衡 | 偏冷 (-250K) | 偏暖 (+400K) | 中性 | **微暖 (~+200-500K)** |
| 影调 | 感知增强中灰反差 | 柔和过渡低对比 | 柔和 | **清晰锐利、对比度中等偏高** |

**Positive Film 在预设空间中占据独特位置：** 高饱和 + 蓝调增强 + 直出感强，与 HNCS（自然准确）、Gold 200（暖金）、5219（电影调色）均不重叠。

---

## 3. Negative Film 色彩特征

### 3.1 历史与官方描述

- **2022 年冬**：首发于 GR III Diary Edition 限量版
- **2023-01-20**：FW 1.70 (GR III) / 1.20 (GR IIIx) 下放至普通版 ✅ 确证
- **官方描述**："用于各类底片的色彩，实现了底片打印照片的**褪色**和**清晰色彩**的完美结合"
  - 「褪色」：饱和度降低、对比度降低
  - 「清晰色彩」：虽然整体褪色，但特定色系保持鲜明 → **不是简单的全局降饱和**

### 3.2 色彩特征（⚠️ 多数为推断，数据严重不足）

| 维度 | 特征描述 | 可信度 |
|------|---------|--------|
| **饱和度** | 整体明显低于 Standard（官方「褪色」描述一致），但非均匀降饱和。暖色系降幅更大，蓝绿色系相对保留 | ⚠️ 合理推断 |
| **影调曲线** | 对比度降低、黑色位被抬高 (lifted blacks)、高光被压暗 | ⚠️ 合理推断 |
| **色相偏移** | 整体偏暖偏绿，有"怀旧底片扫描"质感。绿色和青色保留较好 | ⚠️ 合理推断 |
| **白平衡** | 偏暖（~5800-6200K 推断），比 Positive Film 更偏黄绿 | ⚠️ 推断 |

### 3.3 首个基于 Negative Film 的社区配方（✅ 确证 — Round 2 补充）

从 Ricoh Recipes **Adventure Collection** (2025-02) 获取：

```
「1986 Negative」 Recipe:
Effect: Negative Film
Saturation: +4      Hue: -2       High/Low Key: -1
Contrast: +2        Cont(H): +2   Cont(S): -3
Sharpness: -1       Clarity: -2
Highlight Correction: On   Shadow Correction: Auto
WB: CT 6700K        WB Comp: B:10 G:8
描述: "Vintage yet vibrant, reminiscent of Kodak Gold 200 (1986)"
```

**关键推断：**
- Negative Film 是一个**饱和度可塑性极大的基底**（Saturation +4 仍不出界），暗示基线饱和度极低
- Contrast(Shadow) = -3，与 Positive Film 配方一致的暗部对比度降低趋势
- WB 设定为 CT 6700K + 蓝色偏移 (B:10)，暗示 Negative Film 基线可能偏暖/偏黄绿

### 3.4 仍然存在的数据缺口 🔴

- 仅 1 个基于 Negative Film 的配方，远少于 Positive Film 的 8 个
- **无同一场景 Standard vs Negative Film 的对比样张** — 需持有 GR III 相机自行拍摄
- **「褪色+选择性保色」的量化机制完全未知** — 哪些色相保留、哪些衰减、衰减曲线形状？

### 3.5 与 Fujifilm Classic Negative 的对比

| 维度 | Ricoh Negative Film | Fujifilm Classic Negative |
|------|--------------------|--------------------------|
| 基础设计 | 模拟底片**打印照片**的褪色 | 模拟彩色负片**底片本身**的色彩特性 |
| 饱和度 | 降低但保留特定色系清晰度 | 大幅降低，整体灰度更高 |
| 对比度 | 中等降低，暗部 lifted | 大幅降低，高对比度场景下暗部极灰 |
| 绿色表现 | 保留较好 | 标志性偏青绿 |
| 整体氛围 | "怀旧但不脏" | "胶片味、低保真" |

---

## 4. 逆向工程方法论

### 4.1 五条路径评估

| 方法 | 技术路线 | 技术成熟度 | 所需资源 | 精度 |
|------|---------|-----------|---------|------|
| **A. RAW+JPEG 配对法** 🔴 核心 | 同场景 RAW → 提取线性 RGB；JPEG → 反 gamma 提取处理后的 RGB；拟合色彩变换 | ⚠️ 可行 | GR III 相机 + 色卡 + 场景 | ⭐⭐⭐⭐⭐ |
| **B. 色卡标定法** 🟡 辅助 | ColorChecker 24 色块 RAW/JPEG 对应点 → 多项式回归拟合变换矩阵 | ✅ 成熟 | GR III + ColorChecker | ⭐⭐⭐⭐ |
| **C. DCP 参考法** 🟡 基线 | 提取 Adobe GR III DCP → dcpTool 反编译 → 获取基线色彩矩阵和 ToneCurve | ✅ 成熟 | Adobe Camera Raw 安装 | ⭐⭐⭐ |
| **D. 社区参数推演** 🟢 辅助 | 收集社区配方参数 → 映射到引擎参数空间 → 初始猜测预设 | ❓ 需验证 | 网络搜索 | ⭐⭐ |
| **E. Realme GT 8 Pro 参考** 🟢 验证 | 官方授权复刻样本 → 视觉对比验证 | ❓ 需验证 | 网络搜索 | ⭐⭐ |

### 4.2 最优逆向方法：相机内 RAW 显影 + 色卡标定

**关键发现：Ricoh GR III 支持相机内 RAW 显影，且可以更改 Image Control。** 这意味着：

1. 用 GR III 拍摄一张 RAW (.DNG)
2. 在相机内用 Standard / Positive Film / Negative Film 分别显影，导出 JPEG
3. → 获得**完美像素对齐**的三张 JPEG（同一 RAW、不同 Image Control）

这完全消除了场景差异、曝光差异、白平衡差异等所有外部变量，是逆向工程的理想素材。

**完整流程：**
```
阶段 1: 素材收集（需 GR III 相机）
  ├── 拍摄 ColorChecker Passport + 灰阶卡 + 实景场景的 RAW
  ├── 相机内分别用 Standard/Positive Film/Negative Film 显影导出 JPEG
  └── 记录相机设置（WB=日光固定、ISO、光圈、快门等）

阶段 2: 精确标定
  ├── rawpy/LibRaw 解码 RAW → 线性 sensor RGB
  ├── Standard JPEG 反 gamma → Standard 空间的线性 RGB
  ├── Positive Film JPEG 反 gamma → PF 空间的线性 RGB
  ├── 分离 Image Control 增量 = PF_Transform − Standard_Transform
  └── 用 Colour-Science 拟合 3×3 矩阵 + 影调曲线 + 色相/饱和映射

阶段 3: 引擎参数拟合
  ├── 将 Image Control 增量分解为引擎可表达的参数
  ├── scipy.optimize.least_squares 优化参数
  └── 烘焙 33³ .cube LUT 验证

阶段 4: 验证
  ├── ΔE 色差分析（灰阶、色相环、肤色、天空等关键区域）
  ├── 与社区直出图对比
  └── 与 Realme GT 8 Pro 样张对比
```

### 4.3 立即可做（无需硬件）

1. **获取并分析 GR III DCP 文件** — 从 Adobe Camera Raw 安装目录提取，用 dcpTool 反编译
2. **收集 Positive Film 直出 JPEG 样张** — Flickr 搜索 "Ricoh GR III Positive Film"，下载原图分析影调分布
3. **用引擎做初步猜测** — 基于社区描述创建初始预设，目视对比社区样张

### 4.4 工具链确认

| 工具 | 用途 | 状态 |
|------|------|------|
| dcpTool | DCP ↔ XML 编译/反编译 | ✅ SourceForge |
| LibRaw / rawpy | RAW 解码为线性 RGB | ✅ 成熟开源 |
| Colour-Science (Python) | 色度学计算、ColorChecker 参考值、矩阵拟合 | ✅ 成熟开源 |
| dcraw / RawTherapee | RAW 处理参考 | ✅ 成熟开源 |
| scipy.optimize | 参数拟合 | ✅ 标准科学计算库 |

---

## 5. 引擎适配评估

### 5.1 能力矩阵

| Positive Film 特征 | 引擎可表达？ | 备注 |
|-------------------|------------|------|
| 高饱和度 | ✅ | `global_saturation` |
| 蓝色深度增强 | ✅ | `blue_saturation_boost` + `blue_luminance_shift` + `blue_hue_shift` |
| 中灰反差增强 (contrast > 1.0) | ✅ | `tone.contrast` + `per_channel_contrast` |
| 暗部对比度降低 | ⚠️ | 当前无独立参数，需通过 `shadow_toe_power` + `black_lift` 组合近似 |
| 高光 shoulder 压缩 | ✅ | `highlight_shoulder_start` + `highlight_shoulder_power` |
| 琥珀暖调偏移 | ✅ | `orange_push` |
| 蓝→青蓝色相偏移 | ✅ | `teal_push` |
| 分色调（暗部中性、高光冷蓝） | ✅ | `shadow_tint` / `highlight_tint` |
| 肤色保护 | ✅ | `skin_hue_min/max` + `skin_sat_adjust` |
| WB 暖调偏移 | ✅ | `white_balance_shift_k` |
| **绿色高光抑制** | ❌ | 需要新增参数 |
| **逐色相饱和度映射** | ❌ | 当前仅有全局 + 蓝色特殊处理 |
| **逐色相亮度偏移** | ❌ | 当前仅有蓝色特殊处理 |

### 5.2 可能需要扩展的引擎功能

1. **绿色通道高光抑制** — Negative Film 和 Positive Film 都可能需要在 luma > 阈值时降低绿色通道饱和度
2. **逐色相饱和度映射表** — Negative Film 的「选择性保色」需要比简单的 per-hue-range 更精细的控制
3. **独立暗部对比度** — 当前 `tone.contrast` 是全局参数

---

## 6. 缺口与新问题

### 6.1 已识别缺口

| 缺口 | 严重度 | 解决方式 |
|------|--------|---------|
| **无 GR III RAW+JPEG 配对样本** | 🔴 高 | 需要持有 GR III 相机自行拍摄 |
| **理光未公开 Image Control 默认参数值** | 🔴 高 | 需通过 RAW+JPEG 标定反推 |
| **Negative Film 数据极度不足** | 🟡 中 | 需 GR III 相机拍摄 |
| **Ricoh Recipes 付费配方** | 🟡 中 | 公开 7 个配方已可用，付费配方可用但非必需 |
| **Realme GT 8 Pro 全分辨率样张** | 🟢 低 | 可作验证参考但非核心素材 |

### 6.2 Round 1 → Round 2 已修复的跨文档矛盾

| # | 矛盾 | Round 2 解决方案 |
|---|------|-----------------|
| 1 | Contrast 方向不一致 | 替换为 Ricoh Recipes 7 配方完整数据表 |
| 2 | Hue 调整方向不一致 | 同上 |
| 3 | Cont(Shadow) 方向不一致 | 数据证实 5/7 配方为负 |
| 4 | Positive Film vs Vivid 饱和度 | 标记为待量化验证 |
| 5 | Negative Film vs Standard 饱和度 | 修正为「低于 Standard」+ 添加跨文档矛盾标记 |

### 6.3 未覆盖维度（留待后续）

- **Pentax Custom Image 系统**与 GR Image Control 的底层色彩科学关系
- **Adobe Camera Matching Profile** 是否存在 Ricoh GR 的「Camera Positive Film」等风格
- **GR III 传感器型号和 CFA 光谱响应特性**
- **不同固件版本间 Image Control 的微调**（FW 1.00 → 1.70 → 最新）
- **商业 Lightroom 预设**（VSCO, RNI Films, Mastin Labs）中是否有 Ricoh GR 风格

---

## 7. 初步参数 draft（Positive Film）

基于社区分析推断的初始参数猜测（⚠️ **所有数值未经验证，需在实际标定后调整**）：

```python
PRESET_POSITIVE_FILM_DRAFT = {
    'name': 'ricoh_positive_film',
    'title': 'Ricoh Positive Film (ポジフィルム調) — Draft v1',

    'tone': {
        'black_lift':                0.0045,    # 压缩动态范围：轻微抬升黑位
        'shadow_toe_pivot':          0.10,
        'shadow_toe_power':          0.82,      # 柔和暗部过渡（对应社区 Cont(Shadow) 偏负）
        'contrast':                  1.08,      # 中灰增强反差
        'per_channel_contrast':      [1.00, 0.98, 1.04],  # R中性, G稍低, B最高
        'highlight_shoulder_start':  0.65,      # 较早进入 shoulder（压缩高光）
        'highlight_shoulder_power':  1.30,      # 平滑高光 roll-off
    },

    'color': {
        # 暗部中性，高光冷蓝
        'shadow_tint':             [1.00, 1.00, 1.00],
        'highlight_tint':          [0.97, 0.98, 1.04],     # 高光蓝增强
        'global_saturation':        1.18,                   # 正片高饱和特征
        'highlight_desat_start':   0.65,
        'highlight_desat_max':     0.10,

        # 肤色保护（高饱和下防止猪肝红）
        'skin_hue_min':            12.0,
        'skin_hue_max':            38.0,
        'skin_sat_adjust':         0.90,

        # 标志性色相偏移：蓝→青蓝、红→琥珀
        'teal_push':              3.0,
        'orange_push':             6.0,

        # 理光蓝：深层饱和 + 更深亮度 + 青蓝色相
        'blue_saturation_boost':   1.12,
        'blue_luminance_shift':   -0.03,
        'blue_hue_shift':          4.0,

        # 微暖日光白平衡
        'white_balance_shift_k':  300.0,
    },
}
```

> ⚠️ **注意**：
> - `per_channel_contrast` 中 G=0.98 尝试模拟「高光绿色抑制」，这是近似方案，精确实现需要引擎扩展
> - 所有具体数值为推测范围的中值，实际值待标定后确定
> - Negative Film 暂不提供 draft（数据严重不足）

---

## 8. 下一步行动建议

### 8.1 立即可做（无需硬件）

1. ✅ 从 Adobe Camera Raw 提取 GR III DCP → dcpTool 反编译 → 获取基线色彩矩阵
2. ✅ 从 Flickr 收集 Positive Film 直出 JPEG → 提取影调分布和色彩统计
3. ✅ 用 draft preset 烘焙 LUT → 目视对比社区样张

### 8.2 需要硬件支持（核心路径）

4. 获取/借用 Ricoh GR III/IIIx 相机
5. 拍摄标定素材：
   - ColorChecker Passport 或 SG（在 D65/D50 标准光源下）
   - 中性灰阶卡
   - 高饱和色相环
   - 室外自然场景（蓝天/绿植/肤色/街景）
6. 利用相机内 RAW 显影：一张 RAW → Standard / Positive Film / Negative Film 分别导出 JPEG
7. 按照 §4.2 流程完成精确逆向和参数拟合

### 8.3 引擎扩展（如需）

8. 添加 `green_highlight_suppression` 参数（绿色高光抑制）
9. 添加 per-hue saturation mapping 支持（逐色相饱和度）
10. 添加独立暗部对比度参数

---

## 9. 参考文献

| 来源 | URL | 可信度 |
|------|-----|--------|
| 理光 GR III 官方表现力页（日文，12 种 Image Control） | https://www.ricoh-imaging.co.jp/japan/products/gr-3/feature/03.html | ✅ 官方 |
| 理光 GR III 官方表现力页（中文，10 种） | https://www.ricoh-imaging.com.cn/china/products/gr-3/feature/03.html | ✅ 官方 |
| Ricoh Recipes — The Road Trip Collection | https://ricohrecipes.com/the-road-trip-collection/ | ✅ 社区 |
| Ricoh Recipes — The Street Collection | https://ricohrecipes.com/the-street-collection/ | ✅ 社区 |
| Ricoh Recipes — The Nature Collection | https://ricohrecipes.com/the-nature-collection/ | ✅ 社区 |
| Ricoh Recipes Blog — GR III vs GR IV 色彩差异 | https://ricohrecipes.com/2025/10/24/my-ricoh-gr-iv-arrived-first-recipe-test/ | ✅ 作者实测 |
| Realme GT 8 Pro × Ricoh GR 官方合作 | https://www.dcfever.com/news/readnews.php?id=40277 | ✅ 媒体 |
| Realme GT 8 Pro 5 种 GR Film Tones 样张 | https://www.notebookcheck.net/Stunning-Realme-GT-8-Pro-camera-samples...1135437.0.html | ✅ 媒体 |
| Adobe Camera Raw 添加理光 GR 配置文件 | https://news.mydrivers.com/1/889/889594.htm | ✅ 媒体 |
| 理光中国 GR IIIx 固件页（Negative Film 发布说明） | https://www.ricoh-imaging.com.cn/china/products/gr-3x/firmup/ | ✅ 官方 |
| 知乎: 如何调出 GR2 正片色彩（RGB 曲线还原） | https://zhihu.com/question/522187329/answer/2391304769 | ⚠️ 个人分析 |
| 知乎: GR2 vs GR3 色彩差异 | https://zhihu.com/question/330090419/answer/1402037275 | ⚠️ 社区共识 |
| PConline: GR III HDF 完整参数列表 | https://g.pconline.com.cn/product/dc/ricoh/2170299_detail.html | ⚠️ 第三方 |
| dcpTool (DCP 编译/反编译) | https://sourceforge.net/projects/dcptool/ | ✅ 开源 |
| dcamprof (DNG Camera Profile 工具) | https://github.com/Beep6581/dcamprof | ✅ 开源 |
