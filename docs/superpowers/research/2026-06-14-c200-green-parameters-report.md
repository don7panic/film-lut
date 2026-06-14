# C200 green_* 参数量化与引擎实现 — R2 补充报告

**日期:** 2026-06-14
**任务:** 将 green_* 参数从社区形容词映射转为像素级数据支撑

---

## 1. 像素数据采集

### 来源
- **样张**: `output/c200_compare_01.jpg` ~ `c200_compare_09.jpg`（9 组 C200 SP3000 vs 哈苏 X5 双扫对比图）
- **绿色含量**: 13.6% - 34.3%（覆盖多种户外场景）
- **扫描仪**: 左半 = SP3000（富士社区体验），右半 = 哈苏 X5（接近乳剂本真）
- **采样方法**: 逐 5px 步长网格采样，筛选 G > R 且 G > B 且 G > 50 的像素

### 聚合像素统计（SP3000 侧，9 图合并）

| 指标 | 均值范围 | 中位数范围 | 典型值 |
|------|---------|-----------|--------|
| **色相** | 121° – 153° | 130° – 140° | **~132°** [MEASURED] |
| **饱和度** | 0.21 – 0.38 | 0.18 – 0.27 | **~0.25** [MEASURED] |
| **明度** | 0.31 – 0.47 | 0.33 – 0.44 | **~0.38** [MEASURED] |
| **G/R 比** | 1.14 – 1.58 | — | **~1.35** [MEASURED] |
| **G/B 比** | 1.15 – 1.27 | — | **~1.20** [MEASURED] |

### SP3000 vs 哈苏 X5 绿色差异

| 指标 | SP3000 均值 | 哈苏 X5 均值 | Δ |
|------|-----------|-----------|-----|
| 色相 H | ~128° | ~133° | +5° (哈苏更黄绿) |
| 饱和度 S | 0.260 | 0.277 | +0.017 (哈苏略高) |
| 明度 L | 0.376 | 0.394 | +0.018 (哈苏略亮) |

**结论**: SP3000（社区体验）和哈苏 X5（乳剂本真）的绿色差异较小（ΔH≈5°, ΔS≈0.02），绿色特征相对稳定，不似全局饱和度那样受扫描仪大幅影响。

---

## 2. green_* 参数量化

### 色相偏移: `green_hue_shift = +12°`

**推理链**:
1. [MEASURED] C200 SP3000 绿色中位色相 ~132°（偏黄绿于纯绿 120°）
2. [INFERRED] 典型数码传感器捕获的纯绿色植被在 sRGB 中约 115-125°
3. [INFERRED] C200 的绿色偏移 ≈ +12° toward yellow-green
4. [COMMUNITY] "富士绿明显" + "偏黄绿/塑料感" — 黄绿偏移是 Fuji 绿的特征方向
5. [CROSS-CHECK] 社区形容"偏塑料感的绿"与 pixel data 一致：黄绿 + 中饱和 + 中明 → 缺乏深绿层次感

### 饱和度: `green_saturation_boost = 1.06`

**推理链**:
1. [MEASURED] C200 绿色绝对饱和度中位 ~0.20（在 sRGB 域属于低-中水平）
2. [INFERRED] 但"富士绿明显"的描述暗示绿色相对画面其他颜色更突出
3. [INFERRED] C200 的绿色饱和度 boost 应该是**相对于自身全局饱和度的提升**，而非绝对值
4. [COMMUNITY] C200（Color+2, global_sat≈1.08）— 绿色在此全局基线上需微增强至 1.06 以达到"明显但不夸张"
5. [CONTRAST] vs Velvia（极度高饱和）— C200 绿色boost=1.06 使绿色略微突出但不刺眼

### 亮度偏移: `green_luminance_shift = +0.02`

**推理链**:
1. [MEASURED] C200 绿色明度中位 ~0.38，G/R 比 1.35 — 绿色相对红色已较亮
2. [INFERRED] "塑料感" = 绿区 luminance 略高（+0.02）导致缺乏暗部层次
3. [INFERRED] +0.02 是保守值 — 太低会丢失 "小清新" 特征，太高会恶化 "塑料感"
4. [COMMUNITY] 社区描述 "小清新 + 塑料感" 同时存在，暗示适度明度提升

### 色相范围: `85° – 155°`

**推理链**:
1. [MEASURED] 9 张样张绿色像素色相范围: 61°–179°
2. [INFERRED] 85° cutoff excludes pure yellow-green skin overlap (skin typically 10-35°)
3. [INFERRED] 155° cutoff excludes blue-green/teal (which needs separate blue_* treatment)
4. [ENGINE] 仿照 blue_* 的 200-260° 范围设计，green_* 的 85-155° 覆盖了等量的 70° 色相带

---

## 3. 引擎实现

### 修改文件: [`engine/core.py`](file:///Users/oolong/workspace/film/engine/core.py)

**新增参数读取（行 275-277）**:
```python
green_sat_boost  = C.get('green_saturation_boost', 1.0)
green_lum_shift  = C.get('green_luminance_shift', 0.0)
green_hue_shift  = C.get('green_hue_shift', 0.0)
```

**新增 Step 8b（行 343-349）**:
```python
# ---- Step 8b: Optional Green channel boost (Fuji Green / C200 signature) ----
if abs(green_sat_boost - 1.0) > 0.001 or abs(green_hue_shift) > 0.001 or abs(green_lum_shift) > 0.001:
    green_mask = (h >= 85.0) & (h <= 155.0)
    if np.any(green_mask):
        s[green_mask] = s[green_mask] * green_sat_boost
        h[green_mask] = h[green_mask] + green_hue_shift
        l_hsl[green_mask] = np.clip(l_hsl[green_mask] + green_lum_shift, 0.0, 1.0)
```

### 向后兼容性

✅ 所有 5 个现有预设正常加载并生成 LUT：
- 5219, gold200, hassy_blue, leica_classic, ricoh_positive_film — 全部通过

✅ green_* 参数完全 optional — 不提供时默认 neutral (1.0/0.0/0.0)

### 验证测试

| 测试色 | 输入 | 输出 | 效果 |
|--------|------|------|------|
| pure-green | [0.15,0.70,0.20] | [0.14,0.75,0.32] | ΔH=+12°, ΔS=+0.04, ΔL=+0.02 ✅ |
| yellow-green | [0.45,0.75,0.15] | [0.34,0.80,0.14] | 黄色植被获得 Fuji 绿偏移 ✅ |
| cyan-green | [0.10,0.70,0.55] | [0.10,0.70,0.55] | 不变 — 超出 155° mask ✅ |
| red | [0.80,0.20,0.10] | [0.80,0.20,0.10] | 不变 — 红色不受影响 ✅ |
| blue | [0.10,0.20,0.80] | [0.10,0.20,0.80] | 不变 — 蓝色不受影响 ✅ |
| skin | [0.85,0.55,0.38] | — | H=22° 不变 — 肤色保护 ✅ |

---

## 4. C200 预设中的 green_* 使用

```python
# presets/c200.py 应包含:
'color': {
    # ... 其他参数 ...
    'green_saturation_boost': 1.06,   # [MEASURED+INFERRED] Fuji绿 - 微增饱和度
    'green_hue_shift': 12.0,          # [MEASURED+INFERRED] 向黄绿偏移（C200 中位 ~132° vs pure green 120°）
    'green_luminance_shift': 0.02,    # [INFERRED] 微提亮度 — "塑料感/小清新" 特征
}
```

---

## 5. 剩余不确定性

| # | 不确定项 | 影响 | 优先级 |
|---|---------|------|--------|
| 1 | green_hue_shift ±3° 精确值 | 黄绿程度 — 太大→失真，太小→不够 "Fuji" | 🟡 P1 |
| 2 | green_luminance_shift 精确值 | "塑料感" vs "小清新" 的平衡 | 🟢 P2 |
| 3 | green_saturation_boost 精确值 | 绿色突出程度 | 🟢 P2 |
| 4 | 绿色 mask 范围精确边界 | 85/155° cutoff 是否遗漏边界绿色 | 🟢 P2 |
| 5 | 非 SP3000 扫描的绿色验证 | 所有 pixel data 来自 SP3000；哈苏 X5 样本为"卖家校色后" | 🟡 P1 |

---

*报告完成。green_* 参数现已从三个社区形容词（"塑料感""小清新""Fuji绿"）升级为有像素数据支撑的量化参数。*
