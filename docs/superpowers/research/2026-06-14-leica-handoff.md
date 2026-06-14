# Handoff: Leica 色彩配置逆向工程

**日期:** 2026-06-14
**状态:** 调研完成（3 轮），等待用户审核和后续行动

---

## 在 3 分钟内理解当前状态

### 我们做了什么
对 Leica 的色彩配置体系进行了三轮深度调研，最终从 Adobe 官方页面确认了 Camera Matching 状态。产出一份最终报告。

### 核心结论
1. **Leica 色彩分三层**：Film Styles（5 种·可调）→ FOTOS Leica Looks（7 种·可调强度）→ LUX App Looks（11 种）
2. **Adobe Camera Matching = No** 对几乎所有 Leica 相机（仅 M8 和 V-LUX 5 例外）— 这是最关键的事实发现
3. **第一优先级复刻目标**：Leica Classic Look + M9 CCD Look
4. **逆向入口重排**：小米徕卡 > LUX App > 样张分析 > DCP（大幅降级）

### DCP 路径降级意味着什么
Adobe 的 Leica DCP 文件仅包含传感器基线色彩矩阵（ColorMatrix1/2），**不包含**风格化的 ProfileLookTable/3D LUT。这与 Ricoh GR III（Camera Matching = Yes → 可直接提取 Positive Film 色彩数据）形成根本性对比。Leica 的色彩哲学没有被 Adobe 生态暴露。

### 文档索引
| 文档 | 路径 | 用途 |
|------|------|------|
| **最终报告** | `docs/superpowers/research/2026-06-14-leica-final-report.md` | 完整调研结论 + 行动路线 + 本地 DCP 验证 |
| Round 1 合并 | `docs/superpowers/research/2026-06-14-leica-round1-merged.md` | 详细研究过程 |

### 可立即执行（无需 Leica 相机）

| # | 操作 | 预计耗时 | 收益 |
|---|------|---------|------|
| 1 | 浏览器访问 DPReview Leica M11/M9/Q3 样张画廊，下载 DNG 文件 | 30 分钟 | ⭐⭐⭐⭐ |
| 2 | 安装 Leica LUX App（免费版），用纯色测试图截取各 Look 输出 | 1 小时 | ⭐⭐⭐⭐ |
| 3 | 从 Leica 官网下载 Q3 + SL3 用户手册 PDF，查阅 Film Style 章节 | 5 分钟 | ⭐⭐⭐ |
| 4 | 收集 Xiaomi 17 Ultra 徕卡滤镜评测样张 | 20 分钟 | ⭐⭐⭐ |
| 5 | ~~检查 Leica DCP 文件~~ ✅ **已完成** — 本地 Adobe LR 目录确认：仅 M8、V-Lux 5、D-Lux 7、C-Lux 有 Camera Matching profiles。M9/M10/M11/Q3/SL3 仅有 Adobe Standard。Panasonic S5M2 有 17 个 Camera Matching + Leica 联名风格（L Monochrome/L Classic Neo）可作为 SL 系列代理数据。 | — | — |
| 6 | 安装 dcpTool → 反编译 Panasonic S5M2 Camera L Monochrome / L Classic Neo profiles → 提取 LUT 数据 | 15 分钟 | ⭐⭐⭐⭐ |

### 引擎扩展建议
- `vignette_strength` — 暗角
- `green_luminance_boost` — 绿色亮度（M9 CCD 翠绿）
- `per_channel_saturation [R, G, B]` — 逐通道饱和度

### 与现有预设不重叠
M9 CCD **深幽蓝 + 油润翠绿 + 极高微对比** 在 HNCS / Gold 200 / 5219 / Positive Film 中完全独特。

### 主要盲点
- M9 CCD 色彩偏移无量化角度/幅度
- Leica Film Style 的精确参数范围（需手册确认）
- Leica Looks 的实际视觉特征（需 LUX app 对比测试）
- M11 是否有 Film Style 菜单（未确认）
