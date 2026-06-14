# Kodak Gold 200 LUT 色彩忠实度调研报告

**日期:** 2026-06-14
**方法:** deep-investigate（2 轮探索、9 探索者、2 验证者）
**结论:** **存在显著差异，8 个维度中 6 个有问题**

---

## 执行摘要

当前 `gold200` LUT（`presets/gold200.py`）与真实 Kodak Gold 200 胶片在色彩呈现上**存在显著差异**。核心问题集中在四个方面：

| # | 问题 | 严重度 | 影响 |
|---|------|--------|------|
| 1 | **蓝色色相方向错误 + 六重过度压制** | 🔴 P0 | 蓝色偏紫，饱和度降 30-45%，低蓝崩塌为灰 |
| 2 | **整体暖调过度叠加** | 🔴 P0 | 中性灰 N8 偏入橙色区 (H=41°) |
| 3 | **肤色过暖过饱和** | 🔴 P0 | 肤色偏移 +9-11° 入橙区，饱和度 +9-24% |
| 4 | **per_channel_contrast 方向反转** | 🟡 P1 | B 通道 γ 最低，但真实胶片蓝层 γ 应最高 |
| 5 | **饱和度不足** | 🟡 P1 | global_sat=1.02 vs 参照指示应更高 |
| 6 | **绿色渲染缺失** | 🟡 P1 | 引擎无绿色专用参数 |
| 7 | **黄色偏移方向错误** | 🟡 P1 | 60°→55°（偏橙），非「pop」 |
| 8 | **对比度方向可能反了** | 🟢 P2 | 参照指示 Gold 200 对比度应更低 |

---

## 调研方法

### 数据来源
| 来源 | 可靠性 | 用途 |
|------|--------|------|
| Python 定量 LUT 分析（直接测量） | **高** | 确认 LUT 对 14+ 种测试色的精确行为 |
| Fuji X Weekly Gold 200 Recipe (Ritchie Roesch) | **中** | 第三方系统化参照（社区最权威 Fuji 仿真源） |
| Dehancer Gold 200 Profile | **中** | 专业胶片仿真工具的官方描述 |
| 彩色负片物理原理（三层乳剂结构） | **高** | per_channel_contrast 方向验证 |
| 5219 校准文档 | **中** | 项目内部方法学参考 |
| 社区评测（知乎/微博/B站/FPP Store） | **低** | 主观感受，用作佐证而非主证据 |

### 限制声明
- **未获取 Kodak E-7022 技术数据表**（特征曲线/光谱敏感度）——多次搜索未果
- **无 Gold 200 + MacBeth 色卡实测数据**——网上无公开的色度学研究
- **第三方参照(Fuji/Dehancer)是仿真层而非 ground truth**——用仿真验证仿真有固有局限
- 因此本报告的「差异」判定基于推理链：LUT 行为 ≠ 第三方参照 ≠ 胶片物理原理，每环有不确定性

---

## 逐维度分析

### D1: 影调曲线

**当前 LUT 参数:**
```python
'black_lift': 0.0020
'shadow_toe_pivot': 0.10, 'shadow_toe_power': 0.86
'contrast': 1.02
'per_channel_contrast': [1.02, 1.00, 0.96]  # R boosted, B reduced
'highlight_shoulder_start': 0.72, 'highlight_shoulder_power': 1.20
```

**差异 1: per_channel_contrast 通道方向可能反转**

当前 LUT：B=0.96 → 蓝通道 γ 最低，中灰处 B 通道反而最亮（R/G/B=0.486/0.493/0.507）
真实胶片物理：彩色负片三层乳剂中，蓝感光层位于**最上层**，通常具有**最高**的对比度/γ
5219 校准参考：B=1.06（最高），符合物理原理

**判定: ⚠️ 方向可能反转**。B 通道应 ≥ R 通道（至少不应是最低）。

**差异 2: 对比度方向与参照矛盾**

| 来源 | 对比度指示 |
|------|-----------|
| 当前 LUT | `contrast=1.02`（略高于线性） |
| 预设文档 | "Higher contrast than Portra — consumer film pop" |
| Fuji X Weekly | **H-2 / S+1**（显著降低对比度！） |

Fuji X Weekly 的 H-2/S+1 表示**降低高光、提升阴影 = 降低整体对比度**。这与我们文档的假设「consumer film pop = 高对比度」矛盾。可能 Gold 200 的「pop」来自高饱和度而非高对比度。

**判定: ⚠️ 需要重新评估**。contrast 方向可能需要反转（<1.0）。

**其他影调参数:** black_lift、shadow_toe、highlight_shoulder 的大致形状合理，无显著差异。

---

### D2: 蓝色表现 — 🔴 P0

**当前 LUT 参数:**
```python
'teal_push': -5.0              # 推离 teal（向品红）
'blue_hue_shift': 5.0          # 向青偏移（？实际推向品红）
'blue_saturation_boost': 0.85  # 降饱和
'blue_luminance_shift': -0.04  # 变暗
'white_balance_shift_k': 1000  # R boost, B cut
+ split-tone shadow_tint B=0.95, highlight_tint B=0.88
+ tone curve per_channel_contrast B=0.96
```

**定量测量:**

| 测试色 | 输入 H | 输出 H | ΔH | ΔS |
|--------|--------|--------|-----|-----|
| 纯蓝 (0,0,1) | 240° | 250° | **+10°（向品红）** | **-30%** |
| 天空蓝 (0.4,0.6,1) | 220° | 233° | **+13°** | **-31%** |
| 中蓝 (0,0,0.7) | 240° | 258° | **+18°** | **-44%** |
| 青 (0,1,1) | 180° | 169° | **-11°（向绿）** | — |

**差异 3: 色相方向错误（🔴 关键）**

- 预期：预设文档描述蓝色应为 "warm, muted, **slightly cyan**"
- 实际：蓝色 240° → 250°，向**品红/紫色**偏移（+10~18°）
- 根因：`teal_push=-5.0` 将蓝色推离 teal(=200°) → 向 240°+ 的方向（即品红），`blue_hue_shift=+5.0` 同向叠加
- 240° + 5° = 245° 是向品红（品红=300°），不是向青（青=180°）

**差异 4: 蓝色被六重削弱**

六种独立机制同时压制蓝色通道：

| # | 机制 | 效果 | 贡献 |
|---|------|------|------|
| 1 | per_channel_contrast B=0.96 | 非线性（power curve） | 中 |
| 2 | shadow_tint B=0.95 | @阴影 → B×0.95 | 低 |
| 3 | highlight_tint B=0.88 | @高光 → B×0.88 | 中 |
| 4 | WB +1000K | 全亮度 B×0.9 | **高** |
| 5 | blue_sat_boost ×0.85 | HSL S×0.85 | **高（最大贡献者 -15%）** |
| 6 | blue_lum_shift -0.04 | HSL L-0.04 | 低 |

低亮度蓝色（≤0.3）完全崩塌为灰色——六个机制叠加后蓝色饱和度损失 30-45%。

**判定: 🔴 两个 P0 问题。**
1. `blue_hue_shift` 符号应为负（-5° 向青，而非 +5° 向品红）
2. `teal_push` 应改为正值（+5.0 推向 teal，而非推离）
3. 六重削弱应精简——`blue_saturation_boost` 可从 0.85 提至 0.95，减少 WB shift 强度

---

### D3: 红色表现

**定量测量:**
- 纯红 (1,0,0) H=0° → H=10°：orange_push=10° 生效 ✅
- 带微量蓝的红 (0.9,0.0,0.1) H=353.3° → H=355°：**不生效**（353° 不在 [0,40] 范围）

**差异 5: 360° wraparound bug**

纯红色 (H=0°) 落入 `[0, 40]` 范围，orange_push 生效。但略带蓝色的红色（H=353~359°）在 hue wraparound 边界外，不被捕获。这是一个边缘情况 bug。

**判定: 🟢 低严重度**。主要逻辑正确，边缘 case 需修复（可用 `(h <= 40) | (h >= 350)` 替代）。

---

### D4: 绿色表现 — 🟡 P1

**定量测量:**

| 测试色 | 输入 H | 输出 H | ΔS |
|--------|--------|--------|-----|
| 纯绿 (0,1,0) | 120° | 120° | 0% |
| 中绿叶 (0.15,0.5,0.08) | 110° | 103° (**-7° 向黄绿**) | **-38%** |
| 亮叶 (0.35,0.85,0.15) | 103° | 91° (**-11° 向黄绿**) | +13% |
| 黄绿叶 (0.10,0.60,0.20) | 132° | 136° (**+4° 远离黄绿**) | -26% |

**差异 6: 绿色方向基本正确但饱和度极不稳定**

- 中亮度绿色因 R boost (per_channel + WB) 确实向黄绿偏移（方向对）
- 但饱和度在不同亮度区间波动剧烈（-38% ~ +13%），没有可控性
- 含 B 分量的绿色反而远离黄绿方向
- 纯绿完全不受影响（无专用参数命中 H=120°）

**差异 7: 绿色渲染缺失**

- 引擎 `apply_color_grade()` 有 blue 专项参数（`blue_saturation_boost`, `blue_hue_shift`, `blue_luminance_shift`），但无对应 green 参数
- 预设文档描述 "yellow-green, warm golden foliage" 未在引擎中得到实现
- Ritchie Roesch (Fuji X Weekly) 明确提到 "Gold 200 is particularly prone to a green cast"——这是 Gold 200 的已知特征

**判定: 🟡 P1 功能缺失**。引擎应添加 `green_hue_shift` 和 `green_saturation_boost` 参数。

---

### D5: 黄色表现 — 🟡 P1

**全步骤追踪（纯黄 1,1,0 H=60°）:**

| 步骤 | H | 贡献 |
|------|---|------|
| Tone curve | 60° (不变) | 0° |
| Split-tone | 58° (-2°) | R×1.08 > G×1.03 |
| **WB shift** | **52° (-6°)** | **R×1.1 → R 主导，向橙偏移** |
| HSL masks | 52° | 不变 |
| Display gamma | 55° | +3° 补偿 |
| **最终** | **55° (-5°)** | |

**差异 8: 黄色被推向橙色而非「pop」**

- 根因：WB shift +1000K（R×1.1）使 R 通道在黄色中相对 G 多 10%，将黄色推向橙色方向
- 预期：Gold 200 以 "Gold" 命名，黄色应该突出/鲜艳
- 实际：黄色 60° → 55°，变得偏暖橙但失去了「亮黄」的 pop 感

**判定: 🟡 P1**。黄色「pop」应通过饱和度增强实现（如增加 yellow 专用 sat boost），而非依赖 WB shift 的副作用。

---

### D6: 肤色渲染 — 🔴 P0

**定量测量:**

| 测试色 | 输入 H | 输出 H | ΔH | ΔS |
|--------|--------|--------|-----|-----|
| 亚洲肤色 (0.9,0.7,0.5) | 30° | 39° | **+9°** | **+24%** |
| 偏冷肤色 (0.8,0.6,0.5) | 27° | 38° | **+11°** | **+31%** |
| 中性灰 (0.7,0.7,0.7) | — | **41°** | — | — |

**差异 9: 肤色偏移过大、饱和度过高**

- `skin_hue_max=40°`：40° 已是纯橙色，远超传统肤色保护范围（通常 10-35°）
- `skin_sat_adjust=1.10`：**增强**肤色饱和度（+10%），专业胶片通常**降低**肤色饱和使皮肤平滑（5219 用 0.88）
- `orange_push=10°`：将肤色额外推 +10° 向橙
- 三重叠加：WB+1000K + orange_push=10° + skin_sat=1.10 → 肤色从 ~27° 推至 37-39°，饱和度增加 9-31%

**差异 10: 中性灰严重偏暖**

N8 灰 (0.7,0.7,0.7) → 输出 (0.806, 0.746, 0.588) → H=41°（进入橙色区！）

这意味着画面中**所有中性色**都被染上暖橙色。WB +1000K 是主导因素（R+10%, B-10%），split-tone warm tint 叠加加重。

**判定: 🔴 P0**。
1. `skin_hue_max` 应从 40° 降至 35°
2. `skin_sat_adjust` 应从 1.10 降至 ≤1.00（保护而非增强）
3. WB shift 应大幅降低或改为固定 Daylight 偏移（参考 Fuji X Weekly: +4R/-5B）

---

### D7: 整体饱和度 — 🟡 P1

| 来源 | 指示 |
|------|------|
| 当前 LUT | `global_saturation=1.02`（仅 +2%） |
| Fuji X Weekly | **Color +3**（显著高饱和） |
| FPP Store | "saturated colors, bright prints" |
| Dehancer | "saturated colors" |
| `highlight_desat_max` | 0.04（极其保守，5219 用 0.15 = 3.75x） |

**差异 11: 饱和度显著不足**

Gold 200 在多个独立来源中被描述为「高饱和」胶片。当前 `global_saturation=1.02` 几乎相当于中性。高光去饱和 0.04 也过弱——真实胶片的高光应更明显地去饱和。

**判定: 🟡 P1**。`global_saturation` 应提高（建议范围 1.10-1.20），`highlight_desat_max` 应提高至 0.10-0.15。

---

### D8: 流水线结构性限制

以下限制来自架构层面，不属于参数错误：

1. **无反转向过程**: 真实负片经历 exposure → negative → C-41 → inversion → scanning。LUT 直接模拟最终外观，无法模拟 orange mask 的非线性去除
2. **无层间串扰 (inter-layer crosstalk)**: 3D LUT 的独立 RGB 无法模拟三层乳剂的光谱交叉敏感性
3. **Rec.709 色域限制**: Gold 200 的金黄色域可能超出 Rec.709
4. **V-Log 阴影死区**: ~12% V-Log 代码映射为纯黑
5. **33³ 精度**: P95 误差 7 LSBs，对强色相偏移可能有可察觉误差

---

## 差异总览

| # | 维度 | 差异描述 | 严重度 | 证据强度 |
|---|------|---------|--------|---------|
| 1 | 蓝色 | 色相偏移方向反了（向品红而非向青） | 🔴 P0 | 高 — 定量确认 |
| 2 | 蓝色 | 六重机制过度压制（饱和度 -30~45%） | 🔴 P0 | 高 — 量化分解 |
| 3 | 肤色 | 过暖过饱和（+9-11°, +9-31% sat） | 🔴 P0 | 高 — 定量+视觉 |
| 4 | 暖调 | 中性灰 N8→H=41°（全局暖偏色） | 🔴 P0 | 高 — 定量+色板 |
| 5 | 影调 | per_channel_contrast B=0.96 方向可能反转 | 🟡 P1 | 中 — 物理原理 |
| 6 | 饱和度 | global_sat=1.02 远低于参照 | 🟡 P1 | 中 — 第三方参照 |
| 7 | 绿色 | 渲染缺失（引擎无绿色专用参数） | 🟡 P1 | 高 — 代码分析 |
| 8 | 黄色 | 被推向橙色（-5°），非「pop」 | 🟡 P1 | 高 — 步骤追踪 |
| 9 | 影调 | contrast 方向可能与参照矛盾 | 🟢 P2 | 低 — 参照不确定 |
| 10 | 红色 | 360° wraparound bug（边缘 case） | 🟢 P2 | 高 — 数学确认 |
| 11 | 高光 | desat_max=0.04 过弱 | 🟢 P2 | 中 — 与 5219 对比 |

---

## 修复建议

### P0 — 立即修复

```python
# presets/gold200.py

# 1. 蓝色色相方向修正
'teal_push': 5.0,              # +5.0 推向 teal（而非 -5.0 推离）
'blue_hue_shift': -5.0,        # -5.0 向青偏移（而非 +5.0 向品红）

# 2. 蓝色压制缓解
'blue_saturation_boost': 0.95, # 从 0.85 提升（保留 muted 但不过度）
'white_balance_shift_k': 400.0,# 从 1000 大幅降低（减少全局暖偏）

# 3. 肤色修正
'skin_hue_max': 35.0,          # 从 40 降至 35（排除纯橙色区）
'skin_sat_adjust': 0.95,       # 从 1.10 降至 0.95（保护/柔化肤色）
```

### P1 — 建议调整

```python
# 4. per_channel_contrast 方向修正
'per_channel_contrast': [1.00, 1.00, 1.02],  # B 通道 γ 应最高

# 5. 饱和度提升
'global_saturation': 1.12,     # 从 1.02 提升
'highlight_desat_max': 0.12,   # 从 0.04 提升

# 6. 对比度重新考虑
'contrast': 0.96,              # 从 1.02 降至 <1.0（参照指示低对比度）
```

### 引擎增强（需开发）

```python
# engine/core.py apply_color_grade() 新增:
# 绿色专用参数（模拟 Gold 200 的 yellow-green foliage）
'green_hue_shift': 0.0,        # 绿色色相偏移（度）
'green_saturation_boost': 1.0, # 绿色饱和度调整
```

### 橙色偏移 wraparound 修复

```python
# engine/core.py 第 330 行:
# 当前:
red_mask = (h >= 0.0) & (h <= 40.0)
# 改为:
red_mask = (h <= 40.0) | (h >= 350.0)  # 覆盖 0°/360° 边界
```

---

## 待验证盲点

| # | 盲点 | 说明 |
|---|------|------|
| 1 | **Gold 200 真实色度学数据** | E-7022 技术数据表（特征曲线/光谱敏感度）未获取。建议线下寻找 PDF 或联系 Kodak Alaris |
| 2 | **ColorChecker 实测对比** | 最理想的验证方式：同一场景用 S9 + LUT 和 Gold 200 胶卷同时拍摄色卡，对比扫描结果 |
| 3 | **Fuji 参数 → 我们的参数的精确映射** | Color +3 映射为 `global_saturation` 的具体数值不确定（范围估计 1.10-1.30） |
| 4 | **contrast 方向确认** | Fuji H-2/S+1 与我们的 `contrast` 参数不是相同的数学操作，需独立验证 |
| 5 | **视觉并排对比** | 需要 Gold 200 实际扫描与 LUT 输出在同一场景的视觉对比 |
| 6 | **33³ 精度实际感知影响** | 理论 P95 误差 7 LSBs 在真实照片中是否可见待验证 |

---

## 附录: 定量分析方法

所有 LUT 定量分析通过以下方式执行：
```bash
cd /Users/oolong/workspace/film
uv run python3 -c "
import numpy as np
from engine.core import apply_tone_curve, apply_color_grade, rgb_to_hsl
from presets.gold200 import PRESET as params
# ... 14+ test colors, 5 gradient dimensions, per-step tracking
"
```

关键测试色涵盖：纯红、橙、黄、绿、青、蓝、品红、中性灰阶梯、肤色渐变、天空蓝渐变、绿叶渐变。

---

## 参考来源

1. **Fuji X Weekly — Kodak Gold 200 Recipe**: `fujixweekly.com/2020/04/16/` (X-Trans IV), `fujixweekly.com/2023/10/24/` (X-Trans V) — Ritchie Roesch
2. **Dehancer — Kodak Gold 200 Film Profile**: `dehancer.com/profiles/film/kodak-gold-200`
3. **Film Photography Project Store — Kodak Gold 200**: `filmphotographystore.com/products/35mm-color-kodak-gold-200-1-roll`
4. **Kodak 5219 Calibration Research** (项目内部): `docs/superpowers/specs/2026-06-13-5219-lut-calibration.md`
5. **彩色负片乳剂结构原理**: 三层乳剂 R/G/B 叠层结构是公认的胶片物理学事实
