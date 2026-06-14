# 富士 C200 色彩逆向工程 — 最终报告

**日期:** 2026-06-14
**状态:** ✅ 完成交付
**方法:** deep-investigate（3 轮探索, 12 位探索者, 2 位 Verifier）

---

## 执行摘要

成功完成了富士 Fujicolor C200（日产老版）的色彩逆向工程。通过 3 轮探索——从社区共识采集到像素级色彩测量、从符号推理到引擎定量验证、从参数猜测到矛盾解决——产出了可直接在 Panasonic S9 相机上使用的 `.cube` LUT 文件。

**核心发现：C200 不是"冷调"胶片。** 它是一个温和暖调的消费级彩色负片，其"偏冷"是相对于 Kodak Gold 200 侵略性暖调的**相对感知**，而非绝对特征。C200 有三大独特签名：**暗部暖红偏移**（阴天发红发紫）、**CCB=Off 的自然蓝色**（Superia 家族中独一无二）、**偏黄绿方向的富士绿**。

---

## 1. C200 色彩 DNA

### 设计哲学

*C200 是一种温和暖调的胶卷，其温暖是克制的。它不是物理学上的冷调，而是一种拒绝过度暖化的设计克制——不推橙、不加蓝深度、自然肤色。这种克制在中国社区中被感知为"偏冷"。*

### 六维色彩画像

| 维度 | 特征 | 引擎实现 | 证据等级 |
|------|------|---------|---------|
| **整体色调** | 微暖（+150K），克制不侵略 | `white_balance_shift_k=+150` | MEASURED |
| **暗部色彩** | 🔥 暖红偏移（C200 独有签名） | `shadow_tint=[1.025,0.995,0.965]`（R+2.5%, B-3.5%） | MEASURED — 7张实拍 |
| **绿色渲染** | 🔥 偏黄绿 +12°，中度饱和，略亮 | `green_hue=+12°, green_sat=1.06, green_lum=+0.02` | MEASURED — 像素采样 |
| **蓝色表现** | 🔥 CCB=Off — 自然深度，不加不减 | `teal_push=0, blue_hue=0, blue_sat=1.02` | MEASURED |
| **肤色** | 自然温暖（19-34°），不推橙 | `skin_hue=14-36°, orange_push=4°, skin_sat=0.98` | MEASURED |
| **影调** | 柔和电影感（contrast=0.96） | H+0.5/S-0.5 映射 | MEASURED |

---

## 2. 参数修正历程

| 参数 | R1 猜测 | R2 修正 | R3 定稿 | 修正原因 |
|------|---------|---------|---------|---------|
| WB | -150K ❌ | +200~400K | **+150K** ✅ | Fuji WB符号约定(-3B=暖) + 实拍R/G=1.350 |
| shadow_tint | G boost ❌ | R boost | **[1.025,0.995,0.965]** ✅ | 6/7照片暗部H=13-52°红/橙 |
| global_sat | 1.06 | 0.95-1.02 | **1.04** ✅ | SP3000悖论解决(哈苏样本"卖家校色") |
| teal_push | 2.0° | 2.0° | **0.0°** ✅ | CCB=Off |
| blue_hue | -1.0° | -1.0° | **0.0°** ✅ | CCB=Off |
| orange_push | 5.0° | 4.0° | **4.0°** ✅ | 肤色自然不推橙 |
| green_* | — | — | **+12°/1.06/+0.02** ✅ | 像素采样(9组双扫对比) |

---

## 3. C200 vs 现有预设 差异矩阵

| 维度 | C200 | Gold 200 | Positive Film | 5219 | HNCS | Leica Classic |
|------|------|----------|---------------|------|------|---------------|
| **WB** | +150K 微暖 | +400K 暖 | -200K 冷 | 中性 | -250K 冷 | +300K 暖 |
| **暗部** | 🔥 暖红 | 暖金 | 中性 | 青蓝 | 中性 | 微暖 |
| **绿色** | 🔥 黄绿+12° | 暖黄绿 | 中性饱和 | 默认 | 自然 | 默认 |
| **蓝色** | 🔥 CCB=Off 自然 | 暖青 (hue=-5°) | 深青 (sat=1.0) | 默认 | 自然深度 | 深青蓝 |
| **饱和度** | 1.04 | 1.12 | 1.18 | 0.90 | 1.00 | 1.08 |
| **对比度** | 0.96 柔和 | 0.96 柔和 | 1.04 | 1.08 | 1.08 | 1.08 |
| **肤色** | 自然温暖 | 暖金（推橙） | 保护 | 最保护 | 中性 | 自然 |
| **橙调** | 4° | 10° | 6° | 2° | 0° | 4° |

---

## 4. 引擎增强

新增 `engine/core.py` 中 green_* 参数（Step 8b），仿 blue_* 模式：

```python
'green_saturation_boost': 1.0,    # 绿色区域饱和度乘数 (H=85-155°)
'green_hue_shift': 0.0,           # 绿色色相偏移（度）
'green_luminance_shift': 0.0,     # 绿色亮度偏移
```

参数为可选，不提供时默认 neutral，不影响现有预设。

---

## 5. 交付物

| 文件 | 说明 |
|------|------|
| [`presets/c200.py`](file:///Users/oolong/workspace/film/presets/c200.py) | 完整预设定义（含证据标注） |
| [`luts/S9_VLog_to_c200.cube`](file:///Users/oolong/workspace/film/luts/S9_VLog_to_c200.cube) | V-Log 输入 LUT（33³, 1.2MB） |
| [`luts/S9_Standard_to_c200.cube`](file:///Users/oolong/workspace/film/luts/S9_Standard_to_c200.cube) | Standard 输入 LUT（33³, 1.2MB） |
| [`test_reference_c200.png`](file:///Users/oolong/workspace/film/test_reference_c200.png) | Before/After 测试参考图 |
| [`engine/core.py`](file:///Users/oolong/workspace/film/engine/core.py) | green_* 引擎参数（新增7行） |
| [`tools/c200_final_calibration.py`](file:///Users/oolong/workspace/film/tools/c200_final_calibration.py) | 全流水线校准脚本（可复现） |

### 研究文档

| 文件 | 说明 |
|------|------|
| `docs/superpowers/research/2026-06-14-c200-color-reverse-engineering-plan.md` | 研究计划 |
| `docs/superpowers/research/2026-06-14-c200-round1-merged.md` | R1 合并报告 |
| `docs/superpowers/research/2026-06-14-c200-round2-merged.md` | R2 合并报告（像素级修正） |
| `docs/superpowers/research/2026-06-14-c200-round3-merged.md` | R3 合并报告（矛盾解决+交付） |
| `docs/superpowers/research/2026-06-14-c200-pixel-measurement.md` | 像素侠 — 像素级色彩测量 |
| `docs/superpowers/research/2026-06-14-c200-d4-d5-deepdive.md` | 蔚然 — 肤色+蓝色深度调研 |
| `docs/superpowers/research/2026-06-14-c200-round2-independent-anchors.md` | 程远 — WB映射+引擎测试 |
| `docs/superpowers/research/2026-06-14-c200-round2-scanner-lut-green.md` | 知远 — SP3000决策+绿色分析 |
| `docs/superpowers/research/2026-06-14-c200-contradiction-resolution.md` | 破局者 — SP3000悖论+冷暖统一 |
| `docs/superpowers/research/2026-06-14-c200-green-parameters-report.md` | 绿植师 — 绿色像素数据+引擎实现 |
| `docs/superpowers/research/2026-06-14-c200-engine-analysis.md` | 浩然 — 引擎参数空间分析 |
| `docs/superpowers/research/2026-06-14-c200-round1-technical-data.md` | 明伟 — 技术数据搜索 |
| `docs/superpowers/research/2026-06-14-c200-community-research-r1.md` | 志远 — 社区评测 |

---

## 6. 已知局限

| # | 局限 | 影响 | 解决方式 |
|---|------|------|---------|
| 1 | **SP3000 vs 乳剂本真** | 预设偏向"社区C200体验"（SP3000扫描风格） | 获取尼康Coolscan/哈苏（非校色）C200扫描后重新标定 |
| 2 | **未经真实C200胶片ColorChecker标定** | 所有参数为像素推断，非物理测量 | 用S9+LUT和C200胶片同时拍摄色卡，对比调整 |
| 3 | **欠曝行为未模拟** | i50mm描述"欠曝时反差增大+饱和度上升"未在引擎中建模 | 需实测此行为，决定是否新增曝光相关参数 |
| 4 | **Classic Negative黑盒** | 引擎通过shadow_tint/highlight_tint/WB proxy Classic Negative效果，保真度未验证 | 需Fuji相机Classic Negative输出与引擎输出做并排对比 |
| 5 | **绿色样本有限** | 绿色像素数据来自9组室内/人像对比图，缺少纯风景/植被场景 | 补充风景类C200样张的绿色区域分析 |

---

## 7. 使用方式

```bash
cd /Users/oolong/workspace/film

# 生成 LUT
uv run python lutex.py --preset c200

# 生成 LUT + 测试预览图
uv run python lutex.py --preset c200 --preview

# 应用到照片
uv run python lutex.py --preset c200 --apply your_photo.jpg

# 应用到 V-Log 照片
uv run python lutex.py --preset c200 --apply your_photo.jpg --apply-type vlog
```

将生成的 `.cube` 文件复制到 S9 的 SD 卡 LUT 目录即可在机内加载。

---

*本报告为 Fujifilm C200 色彩逆向工程研究项目的最终交付物。*
