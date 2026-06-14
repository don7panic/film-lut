# 色彩引擎分析师报告 — 预设对比、引擎参数空间 & C200 初探

**日期:** 2026-06-14
**分析范围:** 5 个现有预设 + engine/core.py 完整参数空间
**目标:** 为富士 C200（日产老版）逆向工程提供技术基础

---

## 任务 A: 现有预设参数对比分析

### A.1 完整参数对比表

| 参数 | 5219 | Gold 200 v2 | HNCS (Hassy) | Positive Film | Leica Classic |
|------|------|-------------|-------------|---------------|---------------|
| **Tone** | | | | | |
| `black_lift` | 0.0018 | 0.0020 | 0.0040 | 0.0 | 0.0020 |
| `shadow_toe_pivot` | 0.12 | 0.10 | 0.12 | 0.08 | 0.10 |
| `shadow_toe_power` | 0.82 | 0.86 | 0.85 | **0.90** (最高) | 0.84 |
| `contrast` | 1.08 | **0.96** (最低) | 1.08 | 1.04 | 1.08 |
| `per_channel R/G/B` | 1.02/1.00/**1.06** | 1.00/1.00/1.02 | 1.00/1.00/1.00 | 1.00/1.00/1.00 | 1.00/0.98/**1.04** |
| `highlight_shoulder_start` | 0.72 | 0.72 | 0.68 | **0.65** (最早) | 0.68 |
| `highlight_shoulder_power` | 1.25 | 1.20 | **1.35** (最强) | 1.30 | 1.30 |
| **Color** | | | | | |
| `shadow_tint [R,G,B]` | [1.00,1.00,**1.03**] | [1.03,1.01,**0.95**] | [1.005,1.00,1.00] | [1.00,1.00,1.00] | [1.02,1.00,**0.97**] |
| `highlight_tint [R,G,B]` | [1.03,0.99,0.96] | [1.06,1.02,0.90] | [1.00,1.00,1.00] | [0.97,0.98,**1.04**] | [0.99,1.00,**1.03**] |
| `global_saturation` | 0.90 | 1.12 | 1.00 | **1.18** (最高) | 1.08 |
| `highlight_desat_start` | 0.60 | 0.68 | 0.62 | 0.65 | 0.65 |
| `highlight_desat_max` | 0.15 | 0.12 | 0.10 | 0.10 | **0.08** (最低) |
| `skin_hue_min/max` | 10-35 | 12-35 | 10-38 | 12-38 | 12-38 |
| `skin_sat_adjust` | **0.88** (最保护) | 0.95 | 0.94 | 0.90 | 0.92 |
| `teal_push` | 3.0 | 5.0 | 0.0 | 3.0 | 3.0 |
| `orange_push` | 2.0 | **10.0** (最强) | 0.0 | 6.0 | 4.0 |
| `blue_saturation_boost` | — (default 1.0) | 0.95 | 1.05 | **1.00** (was 1.08) | 1.08 |
| `blue_luminance_shift` | — (default 0.0) | -0.04 | -0.02 | **0.0** (was -0.01) | -0.03 |
| `blue_hue_shift` | — (default 0.0) | **-5.0** (向青) | **0.0** (removed) | 2.0 | 3.0 |
| `white_balance_shift_k` | — (default 0.0) | **+400** (最暖) | **-250** (最冷) | -200 | +300 |

### A.2 设计哲学聚类

```
                    warm ────────────────────────────── cool
                      │                                    │
       Gold 200 (+400K)                              HNCS (-250K)
       5219 (neutral)                                Positive Film (-200K)
       Leica Classic (+300K)
                      │                                    │
           暖调 / 金色 / 琥珀                         冷调 / 蓝青 / 洁净

                    high sat ──────────────────────── low sat
                      │                                    │
       Positive Film (1.18)                         5219 (0.90)
       Gold 200 (1.12)                              HNCS (1.00)
       Leica Classic (1.08)
                      │                                    │
           反转片 / 鲜艳                           电影卷 / 自然

                    stylized ───────────────────── neutral/accurate
                      │                                    │
       Gold 200 (teal+5, orange+10)                HNCS (teal=0, orange=0)
       Positive Film (teal+3, orange+6)             5219 (teal+3, orange+2)
       Leica Classic (teal+3, orange+4)
                      │                                    │
           强风格化色调偏移                        追求准确再现
```

### A.3 每个预设的设计哲学摘要（从文档注释提取）

| 预设 | 灵魂特征 | 核心差异化 |
|------|---------|-----------|
| **5219** | 柔和电影感，3-layer emulsion contrast (B=1.06 最高)，cyan-biased shadows | 唯一使用 per_channel B 最高 + 无 blue_* 扩展参数 |
| **Gold 200** | "Gold" = 琥珀红 + 金黄 + 暖青蓝，consumer film pop | orange_push=10.0（最强），warm WB +400K |
| **HNCS** | "Natural but better than accurate"，中灰对比增强，neutral 分色调 | 唯一 teal_push=orange_push=0.0，engine 唯一 truly neutral 预设 |
| **Positive Film** | 反转片高饱和 + deep cyan blue + amber red | global_sat=1.18（最高），cool WB -200K |
| **Leica Classic** | 微暖 + 中高对比 + deep cyan blue + 自然肤色 | per_channel G=0.98（唯一降绿），highlight_desat_max=0.08（最低=最保留高光色彩） |

### A.4 关键参数极值观察

- **最低 contrast**: Gold 200 @ 0.96 → 低对比度柔和风格
- **最高 global_sat**: Positive Film @ 1.18 → 反转片高饱和
- **最强 warm WB**: Gold 200 @ +400K
- **最强 cool WB**: HNCS @ -250K
- **最强 orange_push**: Gold 200 @ 10.0°
- **最强 blue 压制**: Gold 200 @ sat=0.95 + hue=-5.0° + lum=-0.04
- **最强 blue 增强**: Leica Classic @ sat=1.08 + hue=3.0° + lum=-0.03
- **最保护高光色彩**: Leica Classic @ desat_max=0.08
- **最保护肤色**: 5219 @ skin_sat=0.88

---

## 任务 B: 引擎参数空间分析

### B.1 已支持操作清单（附行号）

| 类别 | 操作 | 引擎行号 | 说明 |
|------|------|---------|------|
| **Tone** | `black_lift` | L146 | 胶片基底抬升（minimum floor） |
| | `shadow_toe_pivot` | L150-154 | 暗部压缩起始阈值 |
| | `shadow_toe_power` | L150-154 | <1 = 提亮暗部（softer toe） |
| | `contrast` | L158-159 | 全局中灰对比度（power curve） |
| | `per_channel_contrast [R,G,B]` | L157-159 | 逐通道对比度（模拟三层乳剂） |
| | `highlight_shoulder_start` | L162-168 | 高光压缩起始点 |
| | `highlight_shoulder_power` | L162-168 | >1 = 压缩高光（roll-off） |
| | 全局 re-normalize | L171-173 | 防止溢出 1.0 |
| **Split-tone** | `shadow_tint [R,G,B]` | L288-296 | 暗部 RGB 乘数（亮度加权） |
| | `highlight_tint [R,G,B]` | L288-296 | 高光 RGB 乘数（亮度加权） |
| **WB** | `white_balance_shift_k` | L299-304 | ±K → R↑/B↓ 或 R↓/B↑（线性近似） |
| **HSL - Global** | `global_saturation` | L310 | 全局饱和度缩放 |
| | `highlight_desat_start` | L313-317 | 高光去饱和起始亮度 |
| | `highlight_desat_max` | L313-317 | 纯白处最大去饱和度 |
| **HSL - Skin** | `skin_hue_min/max` | L320-324 | 肤色保护色相范围 |
| | `skin_sat_adjust` | L324 | 肤色饱和度乘数（<1=柔化保护） |
| **HSL - Hue push** | `teal_push` | L327-329 | 蓝区→青偏移（含方向自动判断） |
| | `orange_push` | L331-333 | 红区→琥珀偏移（含 360° wraparound） |
| **HSL - Blue** | `blue_saturation_boost` | L336-341 | 蓝区(200-260°)额外饱和度（optional） |
| | `blue_luminance_shift` | L336-341 | 蓝色亮度偏移 |
| | `blue_hue_shift` | L336-341 | 蓝色色相偏移 |

### B.2 引擎缺失但 C200 可能需要的能力

| # | 缺失能力 | C200 需求关联 | 严重度 | Workaround |
|---|---------|-------------|--------|-----------|
| 1 | **Green channel boost** (`green_saturation_boost`, `green_hue_shift`, `green_luminance_shift`) | 🔴 "富士绿" 是 C200 核心特征 — 目前引擎只有 blue_* 专项参数 | **P0** | 暂用 `global_saturation` + `per_channel_contrast G` + split-tone 间接影响，但不够精确 |
| 2 | **Per-channel saturation [R,G,B]** | 🟡 逐通道独立饱和度控制，而非仅全局+蓝色专项 | P1 | 无直接替代 |
| 3 | **Shadow color cast** (独立于 split-tone) | 🟡 暗部绿色偏移需要精确的暗部色相控制 | P1 | `shadow_tint` 可 workaround（G boost in shadow） |
| 4 | **Highlight color cast** | 🟡 阴天"发红发紫"现象可能出现在高光区 | P2 | `highlight_tint` 可 workaround |
| 5 | **Vibrance**（智能饱和度，保护肤色） | 🟢 可选 — C200 肤色需要"生动"表现 | P2 | `skin_sat_adjust` 可部分 workaround |
| 6 | **Global cool/warm** (比 WB shift 更精细) | 🟢 可选 — C200 整体冷调 | P3 | `white_balance_shift_k` 已可用 |
| 7 | **Midtone color cast** (独立于 shadow/highlight) | 🟢 可选 — 中灰区色调独立控制 | P3 | 无直接替代 |

### B.3 建议新增引擎参数

```python
# === P0 建议（C200 核心需求）===

# engine/core.py apply_color_grade() 中新增（仿照 blue_* 模式）:
# 行 ~337 之后：
'green_saturation_boost': 1.0,    # 绿色区域饱和度乘数 (H=85-155°)
'green_hue_shift': 0.0,           # 绿色色相偏移（度，>0 向黄绿，<0 向青）
'green_luminance_shift': 0.0,     # 绿色亮度偏移

# === P1 建议（通用增强）===

# Step 4.5 新增（在 global_sat 之后、按色相分段增强之前）:
'per_channel_saturation': [1.0, 1.0, 1.0],  # 逐通道饱和度乘数 [R,G,B]

# Step 1.5 新增（在 split-tone 之后）:
'midtone_tint': [1.0, 1.0, 1.0],  # 中灰区 RGB 乘数
```

### B.4 结合 C200 特征的引擎覆盖度评估

C200 已知特征 vs 引擎能力矩阵：

| C200 特征 | 引擎表达 | 覆盖度 | 说明 |
|-----------|---------|--------|------|
| 整体冷调 | ✅ `white_balance_shift_k` 负值 | 90% | WB shift 是简化 Kelvin 近似，非精确色适应变换 |
| 暗部绿色偏移 | ⚠️ `shadow_tint` G 通道抬升 | 70% | G boost 在暗部可产生绿色偏移，但非精确 HSL 级控制 |
| 富士绿渲染 | ❌ 需新增 `green_*` 参数 | 30% | `per_channel_contrast G` 可间接影响，但不精确 |
| 生动肤色 | ✅ `skin_sat_adjust` + `skin_hue` | 85% | 充分覆盖 |
| 蓝色深度 | ✅ `blue_saturation_boost` + `blue_hue_shift` | 95% | 最完善的色相专项控制 |
| 影调柔和 | ✅ `contrast` + `shadow_toe` + `highlight_shoulder` | 95% | 充分覆盖 |
| 高光色彩保持 | ✅ `highlight_desat_max` | 90% | 充分覆盖 |
| 阴天"发红发紫" | ⚠️ 难以精确模拟 | 40% | 可能是扫描仪 artifact，非胶片固有特征 |

**整体覆盖度估计: ~70-75%**（若新增 green_* 参数可达 ~85%）

---

## 任务 C: C200 预期参数空间初始猜测

### C.1 设计推导逻辑

基于下列社区共识推导 C200 的参数空间：

1. **整体冷调**: C200 相对 Kodak 偏冷 → WB shift 应为负值
2. **暗部绿色**: "富士胶卷特有的暗部绿色" → `shadow_tint` G 通道提升
3. **富士绿**: 饱和度较高、偏黄绿 → 需 green 参数（暂通过 per_channel G 和整体策略模拟）
4. **肤色生动**: 阴天比 Kodak 肤色好 → `skin_sat_adjust` ≈ 0.95（轻微增强保留生动感）
5. **饱和度介于 Velvia 和 Provia 之间**: → `global_saturation` ≈ 1.05-1.10
6. **光影柔和**: → `contrast` ≤ 1.0, `shadow_toe_power` 较高（柔和 toe），`highlight_shoulder_power` 中等
7. **蓝色有深度但不突出**: 不同于 Positive Film 的富蓝，也不同于 Gold 200 的暖青蓝 → `blue_saturation_boost` ≈ 1.02-1.05
8. **vs Gold 200**: 整体偏冷、绿色更突出、蓝色更深、橙色调更弱、白平衡偏冷
9. **vs Positive Film**: 饱和度更低、影调更柔和、蓝色更内敛、对比度更低
10. **vs 5219**: 饱和度更高、冷调而非中性、绿色更突出、对比度相似或略低

### C.2 初始猜测参数 [ALL GUESS]

```python
"""
Fujifilm Fujicolor C200 (Japan) — Draft v1 [GUESS]
=====================================================
Based on community descriptions and cross-referencing with
existing presets. NOT YET CALIBRATED against actual C200 scans.

Design philosophy (from community consensus):
  1. Overall cool tone — Fuji's signature cool palette, colder than Kodak
  2. "Fuji Green" — distinctive green in shadows and foliage, slightly yellow-green
  3. Soft, cinematic light and shadow — gentle contrast with smooth transitions
  4. Vivid but not overbearing color — saturation between Provia and Velvia
  5. Asian skin tone friendly — "生动再现亚洲人的肤色"
  6. Deep, neutral-cool blues — not cyan-shifted like Gold 200, not overboosted like Positive Film
  7. Shadow areas have a subtle green cast — "富士胶卷特有的暗部绿色"

Key differentiators from existing presets:
  vs Gold 200: cooler WB, greener shadows, less orange, deeper blue
  vs Positive Film: less saturated, softer contrast, subtler blue
  vs 5219: more saturated, cooler WB, greener shadows
  vs HNCS: cooler, more stylized, green shadow signature
  vs Leica Classic: cooler, less contrast, greener shadows instead of warm

⚠️ ALL VALUES ARE INITIAL GUESSES — need calibration against:
   - C200 actual film scans (Flickr/LOFTER sample analysis)
   - Fuji X Weekly Superia recipe proxy comparison
   - Analogica Lab C200 LUT behavioral analysis
   - Community comparison reviews (DCFever, etc.)
"""

PRESET = {
    'name': 'c200',
    'title': 'Fujifilm Fujicolor C200 (Japan) — Draft v1',

    'tone': {
        # Soft, cinematic light and shadow — gentle contrast
        # C200 = "光影柔和却充满故事感" → softer transitions
        'black_lift':                0.0015,       # [GUESS] Minimal film base (C200是消费级低成本胶片)
        'shadow_toe_pivot':          0.10,
        'shadow_toe_power':          0.88,         # [GUESS] 柔和暗部 toe — "光影柔和"
        'contrast':                  0.98,         # [GUESS] 略低于中性，柔和影调（参考 Gold 200 @ 0.96）
        'per_channel_contrast':      [1.00, 1.02, 1.00],  # [GUESS] G 通道略增强 → 绿色对比度 + Fuji绿
        'highlight_shoulder_start':  0.70,         # [GUESS] 较早的高光滚降
        'highlight_shoulder_power':  1.20,         # [GUESS] 中等滚降力度
    },

    'color': {
        # Shadow green cast — THE signature C200 trait
        # "富士胶卷特有的暗部绿色"
        'shadow_tint':             [0.97, 1.04, 0.97],     # [GUESS] G boost +4% in shadow, R/B slight cut
        'highlight_tint':          [0.99, 1.00, 1.02],     # [GUESS] Slight blue boost in highlights

        # Saturation between Velvia and Provia — vivid but not extreme
        'global_saturation':        1.06,                   # [GUESS] 略高于中性，不到反转片级别

        # Moderate highlight desaturation — film's natural roll-off
        'highlight_desat_start':   0.65,
        'highlight_desat_max':     0.10,                   # [GUESS] 中等去饱和

        # Asian skin tone protection — "生动再现" not "猪肝红"
        'skin_hue_min':            12.0,
        'skin_hue_max':            35.0,                   # [GUESS] Standard range
        'skin_sat_adjust':         0.97,                   # [GUESS] 轻微保护，保持"生动"

        # Subdued hue shifts — C200 is less stylized than Gold 200
        'teal_push':               2.0,                    # [GUESS] Subtle blue→cyan (Fuji cool signature)
        'orange_push':             5.0,                    # [GUESS] Moderate red→amber (less than Gold's 10°)

        # ---- Fuji Blue — deep, natural-cool, not overboosted ----
        'blue_saturation_boost':   1.03,                   # [GUESS] Modest deep blue
        'blue_luminance_shift':   -0.02,                   # [GUESS] Slightly deeper blues
        'blue_hue_shift':         -1.0,                    # [GUESS] Very slight blue→cyan

        # Cool baseline — Fuji's signature cool palette
        # C200 is known to be cooler than Kodak (opposite of Gold 200's +400K)
        'white_balance_shift_k': -150.0,                   # [GUESS] Moderate cool (between HNCS -250 and neutral)
    },
}
```

### C.3 猜测依据解释

| 参数 | 值 | 推理链 |
|------|-----|--------|
| `contrast = 0.98` | <1.0 柔和 | "光影柔和" — 用户描述；C200 是平价消费负片，非高对比度反转片 |
| `per_channel G = 1.02` | G 略高 | 增强绿色通道对比度 → 辅助"富士绿"感知 + 暗部绿色偏移的基础 |
| `shadow_tint = [0.97, 1.04, 0.97]` | G 暗部 +4% | "富士胶卷特有的暗部绿色" — G 通道在暗部增强，R/B 微降以突出绿色偏移 |
| `global_saturation = 1.06` | 中等偏上 | 介于 Positive Film (1.18) 和 HNCS (1.00) 之间；"色彩稍重，类似于 Velvia" 但非真正高饱和反转片 |
| `orange_push = 5.0` | 中等 | 比 Gold 200 (10°) 弱，比 5219 (2°) 强 — C200 有一定暖调但不是核心特征 |
| `blue_hue_shift = -1.0` | 微向青 | 富士冷调蓝色 +1° 向青，非常克制（不是 Gold 的 -5° 也不是 Leica 的 +3°） |
| `WB = -150K` | 微冷 | 整体偏冷但不过分（HNCS 在 -250K），体现富士 vs 柯达的温差 |
| `skin_sat_adjust = 0.97` | 近中性 | "生动再现" → 不应过度保护/柔化，保持肤色鲜活 |
| `highlight_desat_max = 0.10` | 中等 | 高光保留部分色彩，不如 5219 的 0.15 强去饱和 |

### C.4 与现有预设的差异预测

| 维度 | Gold 200 | Positive Film | **C200 [GUESS]** | 差异点 |
|------|----------|---------------|------------------|--------|
| WB | +400K 暖 | -200K 冷 | **-150K 冷** | 与 Positive Film 最接近方向但更温和 |
| 暗部偏移 | warm golden | neutral | **green cast** | 🔥 C200 独有特征 |
| 绿色渲染 | yellow-green | neutral-saturated | **Fuji green (more sat, yellow-green)** | 🔥 需新 green 参数 |
| 蓝色 | warm cyan (hue=-5°) | deep cyan (sat=1.00) | **deep natural-cool (hue≈-1°)** | 介于两者之间 |
| 饱和度 | 1.12 | 1.18 | **1.06** | 更接近 Leica Classic (1.08) |
| 对比度 | 0.96 | 1.04 | **0.98** | 与 Gold 200 接近的柔和方向 |
| 肤色 | warm golden | protected | **vivid-natural** | 独特 — 生动但不暖金 |

### C.5 关键不确定性 [需在校准中解决]

| # | 不确定性 | 影响参数 | 解决方式 |
|---|---------|---------|---------|
| 1 | 暗部绿色偏移的精确色相和强度 | `shadow_tint` G | 分析 C200 实际扫描的暗部色板 |
| 2 | "富士绿" 的精确 HSL 特征 | `green_*`（需新增） | 分析 C200 样张中的绿色区域 |
| 3 | 阴天"发红发紫"是胶片特征还是扫描 artifact | 可能影响 `highlight_tint` / `shadow_tint` | 区分 SP3000 vs 哈苏扫描 |
| 4 | 实际对比度水平 | `contrast`, `shadow_toe_power` | 需要特征曲线数据或直方图分析 |
| 5 | 蓝色深度 vs 冷调的来源 | `blue_*`, `WB` | 分析 C200 天空/蓝色物体区域 |
| 6 | 新生代 Fujicolor 200（美产）≠ C200（日产） | 全部参数 | 必须严格区分数据来源 |

---

*本报告为 deep-investigate Phase 1 输出的一部分，为后续 Round 1-10 探索提供技术基准。*
