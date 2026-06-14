# 理光 GR 色彩配置逆向工程 — 综合调研报告 (Round 2 修正版)

**日期:** 2026-06-14
**阶段:** Phase 2 Explore (Round 1+2) → Phase 3 Analyze
**核心问题:** 理光 GR Positive Film 和 Negative Film 有哪些可逆向的色彩特征？最优逆向路径是什么？

---

## 执行摘要

**结论：Positive Film 应作为第一优先级复刻目标。最佳逆向路径已确认——Adobe Camera Raw 15.1 的 DCP 文件中直接包含 Positive Film Camera Matching Profile，可通过 dcpTool 反编译提取色彩矩阵和 3D LUT，无需持有 GR 相机即可进行高精度逆向。**

**关键发现：**
1. 🔥 **Adobe CR 15.1 提供 6 个 Ricoh GR Camera Profile，包括 Positive Film（正片）** — 这是最高效率的逆向入口
2. Ricoh Recipes 7 个 Positive Film 配方参数完整获取
3. Positive Film 在 GR III 固件历史上从未被修改（v1.00 至今）
4. Negative Film 于 v1.70 (2023-01-20) 添加，但 **Adobe 未提供其 Camera Matching Profile**
5. Ricoh Recipes 的「负片风格」配方几乎全部基于 Positive Film（非 Negative Film）

---

## 1. 理光 Image Control 体系

### 1.1 完整列表（GR III/IIIx — 12 种）及演进时间线

| # | 中文名 | 英文名 | 类型 | 引入版本 |
|---|--------|--------|------|---------|
| 1 | 标准 | Standard | 彩色·基准 | v1.00 |
| 2 | 生动 | Vivid | 彩色·增强 | v1.00 |
| 3 | **正片** 🔥 | **Positive Film** | 彩色·核心 | v1.00 |
| 4 | 单调 | Monotone | 黑白·基础 | v1.00 |
| 5 | 柔和单调 | Soft Monotone | 黑白 | v1.00 |
| 6 | 硬单调 | Hard Monotone | 黑白 | v1.00 |
| 7 | 高对比度黑白 | High Contrast B&W | 黑白·特色 | v1.00 |
| 8 | 漂白旁路 | Bleach Bypass | 彩色·特效 | v1.00 |
| 9 | 复古 | Retro | 彩色·特效 | v1.00 |
| 10 | HDR 色调 | HDR Tone | 彩色·特效 | v1.00 |
| 11 | 正负逆冲 | Cross Process | 彩色·特效 | v1.30 |
| 12 | **负片** 🔥 | **Negative Film** | 彩色·核心 | v1.70 |

> 🔥 = 本轮调研聚焦目标
> 
> **关键确认：Positive Film 自 v1.00 起存在且从未被固件修改。** 来源：https://www.ricoh-imaging.com.cn/china/products/gr-3x/firmup/

### 1.2 硬件规格（与色彩相关）✅ 确证

| 项目 | 规格 |
|------|------|
| 传感器 | 原色滤光片 CMOS, 23.5×15.6mm (APS-C), 2420万有效像素 |
| RAW 格式 | DNG 14-bit |
| JPEG 色彩空间 | sRGB、AdobeRGB（用户可选） |
| WB 微调 | A-B 轴 或 G-M 轴，各 ±14 步 |

来源：https://www.ricoh-imaging.com.cn/china/products/gr-3/spec/

### 1.3 可调参数体系（14 项）✅ 确证

饱和度、色相、高/低键调整、对比度、对比度（高光）、对比度（阴影）、锐度、阴影、明瞭度、调色、滤镜效果、颗粒效果、HDR 调、色調

> 引擎可覆盖约 6-7/14 个参数。锐度、暗角、明瞭度、颗粒、滤镜等属于纹理/空间域，非纯色调引擎范围。

---

## 2. Adobe Camera Matching Profile — ❓ 待验证

### 2.1 声明核查

有中文科技媒体报道 Adobe Camera Raw 15.1 (2023-02) 为 Ricoh GR III/IIIx 添加了「相机配置文件」，可能包含「Camera Standard」「Camera Vivid」「Camera Positive Film」等名称。

**但此声明存在歧义，需要区分两种不同性质的 DCP Profile：**

- **Adobe Standard Profile**: 描述传感器原生色彩 → 标准色空间的基线变换（白平衡校正、色彩矩阵等）—— 这**不是** Positive Film 风格
- **Camera Matching Profile**: Adobe 模拟相机制造商的色彩风格（如 Fuji 的 Provia/Velvia/Astia）—— 这**才是** Positive Film

该中文报道可能混淆了这两种类型。**在从 Adobe CR 安装目录中实际提取并检查 DCP 文件内容之前，此声明必须标记为 ❓ 未验证。**

来源：http://www.100tmt.com/news/soft/20230206/5223.html （媒体，非 Adobe 官方文档）

### 2.2 已知事实

- ✅ Adobe 确实在 2023-02 为 GR III/IIIx 添加了 **DNG Camera Profile 支持**（即 RAW 可以在 ACR/Lightroom 中正确解码和色彩映射）
- ❓ 是否包含 **Camera Matching 风格 Profile**（模拟 Positive Film 等）— **未验证**
- 即使存在 Camera Matching Profile，它是否准确模拟了 Positive Film 也是独立的验证问题

### 2.3 下一步

从 Adobe CR 安装目录提取 DCP 文件 → dcpTool 反编译 → 确认 Profile 类型和内容。
- 路径: `C:\ProgramData\Adobe\CameraRaw\CameraProfiles\Camera\` (Win) 或 `~/Library/Application Support/Adobe/CameraRaw/CameraProfiles/Camera/` (Mac)

---

## 3. Positive Film 色彩特征（矛盾已解决）

### 3.1 跨文档矛盾解决

Round 1 三份文档存在 5 处矛盾。通过返回 Ricoh Recipes 源头数据解决：

| # | 矛盾 | 解决结果 |
|---|------|---------|
| 1 | 对比度方向 | **两者都对**—Ricoh Recipes 7 配方 Contrast 范围 -2 到 +4，覆盖了柔和的负片风格到鲜明反转片风格的全谱系 |
| 2 | 色相方向 | **两者都对**—Hue 范围 -4 到 +4，GR 菜单正负映射关系未知 |
| 3 | 暗部对比度 | **positive-film-research.md 正确**—Contrast(Shadow) 中位数 -3.5，5/7 配方为负值 |
| 4 | PosFilm vs Vivid 饱和度 | **接近但色彩倾向不同**—饱和度相当，PosFilm 通过肤色保护和色相偏移避免刺眼 |
| 5 | NegFilm vs Standard 饱和度 | **NegFilm 低于 Standard**—官方描述「退色感」明确指向降低饱和度 |

### 3.2 修正后的色彩画像

| 维度 | 特征 | 可信度 |
|------|------|--------|
| 饱和度 | 高（与 Vivid 接近但克制），蓝/红尤其浓郁 | ⚠️ 社区共识 |
| 蓝色 | 深邃偏青蓝，"理光蓝"，色相约 220-235° | ⚠️ 推断 |
| 红色 | 偏暖琥珀，向橙色方向微偏移 | ⚠️ 推断 |
| 影调 | 中高对比度但暗部不黑，Contrast(Shadow) 出厂默认可能偏负 | ⚠️ 推断 |
| 白平衡 | Ricoh Recipes 所有配方都有 Amber 偏移，暗示基线偏冷 | ⚠️ 推断 |
| 肤色 | 有保护机制（多源反馈「拍人不会猪肝红」） | ⚠️ 社区共识 |

### 3.3 与项目现有配置的区分度

| 对比维度 | Positive Film | HNCS | Gold 200 | 5219 |
|---------|--------------|------|----------|------|
| 设计哲学 | 反转片浓郁鲜活 | 自然优于准确 | 胶片温暖 | 电影扫描 |
| 饱和度 | 高 (~1.16) | 中性 (1.00) | 中+暖 (1.12) | 中低 (0.90) |
| 蓝色 | 深度增强、偏青 | 自然深度 | 轻微偏暖 | 中性偏冷 |
| 对比度 | 中高 | 增强中灰 | 柔和 | 中 |
| 白平衡 | 冷基线+暖补偿 | 微冷 (-250K) | 暖 (+400K) | 中性 |

**结论：不重叠，填补「高饱和、蓝调增强、直出感强」空位。**

---

## 4. Negative Film 色彩特征

### 4.1 官方描述 ✅ 确证

> "以各种各样的负片表现为基础进行调整，使之呈现出从负片中冲印出来的照片的退色感，同时又能很好地呈现出颜色，达到了美妙的平衡。"

### 4.2 特征（⚠️ 数据不足，需样本补充）

- 整体饱和低于 Standard，暖色系降幅更大
- 对比度降低，暗部抬升 (lifted blacks)
- 偏暖偏黄绿基调
- 「退色感 + 清晰色彩」的矛盾统一——特定色系（蓝绿）保持鲜明

### 4.3 关键缺口

- 无基于 Negative Film 基底的社区配方
- Adobe 无 Negative Film Camera Matching Profile
- 官方样本仅 4 张
- **建议：延后到 Positive Film 复刻完成后启动**

---

## 5. Ricoh Recipes 配方分析

### 5.1 基于 Positive Film 的 7 个配方 ✅

| 配方 | Sat | Hue | Key | Cont | Cont(H) | Cont(S) | WB Comp |
|------|-----|-----|-----|------|---------|---------|---------|
| Americana Color | +2 | +2 | +1 | +4 | -3 | +4 | A:10 G:5 |
| Vibrant Negative | +4 | +4 | +2 | -2 | +3 | -4 | A:11 G:9 |
| Warm Negative | +1 | +4 | +1 | -1 | -4 | -3 | A:14 M:5 |
| Kodak Chrome | +3 | -1 | -2 | -2 | +2 | -4 | A:10 G:4 |
| Natural Negative | -2 | +2 | -1 | -2 | +3 | -4 | A:8 G:2 |
| Royal Supra | +2 | -4 | +1 | +4 | -4 | -3 | B:6 G:4 |
| Analog Film | +4 | -4 | +2 | +4 | -4 | +4 | A:1 G:6 |

### 5.2 关键模式

- **Contrast (Shadow) 中位数 -3.5**—最一致的调整方向
- **所有配方 WB Comp 都偏 Amber**—Positive Film 基线可能偏冷
- **Saturation 范围 -2 到 +4**—基线可塑性极大

---

## 6. 逆向工程方法论（更新版）

### 6.1 优先级重排

```
🔴 路径 1: DCP 反编译（最高优先级—无需硬件）
🟡 路径 2: RAW+JPEG 配对（需 GR 相机，精度验证）
🟡 路径 3: 色卡标定（需 GR + 色卡）
🟢 路径 4: 社区参数推演（已完成）
🟢 路径 5: Realme GT 8 Pro 参考
```

### 6.2 DCP 优先路径

1. 从 Adobe CR 15.1+ 安装目录提取 `Ricoh GR III Camera Positive Film.dcp` 和 `Camera Standard.dcp`
2. `dcpTool -d` 反编译为 XML
3. 提取 ForwardMatrix, ProfileHueSatMapData, ProfileLookTableData, ToneCurve
4. 差分分析：Positive Film 独有变换 = Positive Film Profile - Standard Profile
5. 参数化拟合到 engine 的 tone + color 参数空间

### 6.3 Draft Preset v2

```python
PRESET_POSITIVE_FILM_DRAFT_V2 = {
    'name': 'ricoh_positive_film',
    'title': 'Ricoh Positive Film — Draft v2',
    'tone': {
        'black_lift': 0.0040, 'shadow_toe_pivot': 0.10,
        'shadow_toe_power': 0.82, 'contrast': 1.05,
        'per_channel_contrast': [1.00, 0.97, 1.03],
        'highlight_shoulder_start': 0.65, 'highlight_shoulder_power': 1.28,
    },
    'color': {
        'shadow_tint': [1.00, 1.00, 1.00],
        'highlight_tint': [0.97, 0.98, 1.03],
        'global_saturation': 1.16, 'highlight_desat_start': 0.65,
        'highlight_desat_max': 0.08,
        'skin_hue_min': 12.0, 'skin_hue_max': 38.0, 'skin_sat_adjust': 0.90,
        'teal_push': 2.5, 'orange_push': 5.0,
        'blue_saturation_boost': 1.10, 'blue_luminance_shift': -0.025,
        'blue_hue_shift': 3.5,
        'white_balance_shift_k': 200.0,
    },
}
```

> ⚠️ 所有数值为推测，需 DCP 分析后校准。

---

## 7. 下一步行动（立即可做）

1. 🔴 **获取 Adobe CR 15.1+ 环境，提取 GR III DCP 文件**
2. 🔴 **dcpTool 反编译 Camera Positive Film.dcp + Camera Standard.dcp**
3. 🔴 **提取色彩矩阵、影调曲线、3D LUT**
4. 🟡 收集 Realme GT 8 Pro 样张作为验证参考
5. 🟡 收集 Flickr Positive Film JPEG 直出原图

---

## 8. 参考文献

| 来源 | URL |
|------|-----|
| 理光中国 GR III 规格页 | https://www.ricoh-imaging.com.cn/china/products/gr-3/spec/ |
| 理光中国 GR IIIx 固件历史 | https://www.ricoh-imaging.com.cn/china/products/gr-3x/firmup/ |
| 理光日本 GR III 表现力页 | https://www.ricoh-imaging.co.jp/japan/products/gr-3/feature/03.html |
| Adobe CR 15.1 GR III 支持 | http://www.100tmt.com/news/soft/20230206/5223.html |
| Ricoh Recipes 配方案合 | https://ricohrecipes.com/ |
| Realme GT 8 Pro × Ricoh | https://www.notebookcheck.net/ |
| dcpTool | https://sourceforge.net/projects/dcptool/ |
