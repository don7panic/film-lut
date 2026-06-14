# Handoff: Ricoh GR 色彩配置逆向工程

**日期:** 2026-06-14
**状态:** 调研完成，等待用户审核和后续行动

---

## 在 5 分钟内理解当前状态

### 我们做了什么
对 Ricoh GR 系列的 Positive Film 和 Negative Film 色彩配置进行了两轮深度调研，产生了 4 份文档和 1 份最终报告。

### 核心结论
- **Positive Film 应作为第一优先级复刻**，Negative Film 紧随其后
- 逆向工程最佳路径：相机内 RAW 显影 + 色卡标定 → 3D LUT 拟合 → 引擎参数化
- 当前引擎可覆盖 Positive Film 约 70-80% 特征
- **最大瓶颈：需要实际持有 GR III 相机进行标定拍摄**

### 文档索引
| 文档 | 路径 | 用途 |
|------|------|------|
| **最终报告** | `docs/superpowers/research/2026-06-14-ricoh-final-report.md` | 完整调研结论 + 行动路线 |
| 综合报告（慧，已修正） | `docs/superpowers/research/2026-06-14-ricoh-color-reverse-engineering.md` | 全景总览 + Adobe DCP 声明已修正为 ❓ |
| Positive Film 专题 | `docs/superpowers/research/2026-06-14-ricoh-positive-film-research.md` | Positive Film 详细分析 + draft preset v1 |
| 数据源汇总（源） | `docs/superpowers/research/2026-06-14-ricoh-color-profiles-research.md` | 配方参数 + 方法论 + 工具链 |

### 配方数据统计（已收录）
- **Positive Film 基底配方**: 8 个（含 Adventure Collection 的 Kodamax）
- **Negative Film 基底配方**: 1 个（Adventure Collection 的 1986 Negative）

### 可立即执行（无需 GR 相机）
1. 提取 GR III DCP 文件（从 Adobe Camera Raw 目录）→ dcpTool 分析
2. 从 Flickr 收集 Positive Film 直出 JPEG 做影调分析
3. 用 draft preset（最终报告 §7）烘焙第一版 LUT

### 核心行动（需要 GR 相机）
1. 获取/借用 GR III/IIIx
2. 拍摄 ColorChecker + 灰阶卡 + 场景（锁定 WB=日光）
3. **利用相机内 RAW 显影**：一张 RAW → Standard/PF/NF 三张 JPEG（完美像素对齐）
4. 按最终报告 §4.2 流程进行精确逆向

### 已解决的关键问题
- Round 1 的 5 个跨文档矛盾已通过 Ricoh Recipes 原始数据核实修复
- 可信度标记已修正
- Negative Film 数据不足已明确标注

### 剩余盲点
- Pentax Custom Image 与 GR Image Control 的关系
- **Adobe Camera Matching Profile 是否包含「Camera Positive Film」风格 — ❓ 待实际提取 DCP 验证**（中文媒体报道可能混淆了 Adobe Standard Profile 与 Camera Matching Profile）
- GR III 传感器型号和 CFA 特性
- 固件版本间 Image Control 的微调
- Negative Film 仅 1 个配方，数据严重不足（策略：延后到 Positive Film 复刻完成后启动）
