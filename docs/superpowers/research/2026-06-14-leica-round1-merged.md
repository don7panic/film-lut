# Leica 色彩配置逆向工程 — Round 1 合并工作文档

**日期:** 2026-06-14
**状态:** Round 1+2 合并完成，Verifier R1(GAPS)→R2 补充完成，等待 R2 Verifier
**核心问题:** Leica 有哪些适用范围广的色彩配置？可行的逆向工程路径是什么？

---

## 维度 A: Leica 色彩配置全景

### A.1 三层架构（✅ 跨代理一致确认）

```
Leica 色彩配置体系
├── ① 机内 Film Styles（内置·可调参数 ~3 个）
│   ├── Standard / Vivid / Natural / Monochrome / HC B&W
│   └── 覆盖: Q3/Q3 43/SL3（M11 可能不支持）
├── ② Leica Looks（FOTOS App 下载·7 种固定预设 → FW4.0.0 可调强度）
│   ├── Classic, Contemporary, Vivid, B&W, Eternal, Selenium, Chrome
│   └── 仅支持: Q3/Q3 43/SL3/SL3-S
└── ③ Leica LUX App Looks（iPhone App·11 种，Pro 付费订阅）
    ├── 免费: 5 种色彩模式（同 Film Styles）
    ├── Pro: Classic, Contemporary, Vivid, B&W, I Model A, Eternal, Selenium + 4 未知
    └── Artist Look: Greg Williams
```

**关键区分（✅ Round 2 确认解决）：**
- 慧报告：Leica Looks 是「固定、不可编辑的预设」
- 源报告：FW 4.0.0 起 **可调整 Leica Looks 强度**
- **✅ 确认：** IT之家 FW 4.0.0 报道明确写「允许用户调整 Leica Looks 的强度」→ 这是**全局强度 slider**，各参数（对比度/饱和度等）仍然不可单独调整。
  - 慧正确描述了 FW <4.0.0 的状态
  - 源正确描述了 FW 4.0.0+ 的改进
  - 来源：https://www.ithome.com/0/906/169.htm ✅ 确证

### A.2 Film Styles 详细列表（⚠️ 社区共识，非官方文档）

| # | 英文名 | 可调参数 | 可信度 |
|---|--------|---------|--------|
| 1 | Standard | Contrast, Saturation, Sharpening | ⚠️ |
| 2 | Vivid | 同上 | ⚠️ |
| 3 | Natural | 同上 | ⚠️ |
| 4 | Monochrome | Contrast, Sharpening, Grain | ⚠️ |
| 5 | High-Contrast B&W | 同上 | ⚠️ |

**与 Ricoh GR Image Control 对比：**

| 维度 | Ricoh GR III | Leica Q3/SL3 |
|------|-------------|-------------|
| 风格数 | 12（彩色8+黑白4） | 5（彩色3+黑白2） |
| 可调参数数 | **14** | **~3** |
| 正片/负片类 | ✅ | ❌ |
| 社区配方生态 | ✅ ricohrecipes.com | ❌ 不存在 |
| 官方文档透明度 | ✅ 官方表现力页 | ❌ 极少 |

### A.3 Leica Looks 已知 7 种清单（⚠️ 非官方完整清单）

| # | 名称 | 来源 | 可信度 |
|---|------|------|--------|
| 1 | Leica Classic | LUX 官网 | ✅ |
| 2 | Leica Contemporary | LUX 官网 | ✅ |
| 3 | Leica Vivid | LUX 官网 | ✅ |
| 4 | Leica B&W | LUX 官网 | ✅ |
| 5 | Leica Eternal | LUX 官网 mockup | ✅ |
| 6 | Leica Selenium | LUX 官网 mockup | ✅ |
| 7 | Leica Chrome | DCFever Q3 43 | ✅ |
| - | Leica Blue? | 社区提及 | ❓ 待验证 |

**Look 色彩特征推断（⚠️ 全为推断，无官方技术文档）：**

| Look | 推断特征 | 可信度 |
|------|---------|--------|
| Classic | M 胶片时代色彩，微暖、中高对比、红浓蓝深 | ⚠️ |
| Contemporary | 现代数码 Leica，中性偏冷、肤色自然 | ⚠️ |
| Eternal | 永恒经典，低对比柔和、怀旧褪色 | ⚠️ |
| Selenium | 暖棕/紫棕单色调（暗房硒色调工艺） | ⚠️ |
| Vivid | 类似 Velvia 反转片，蓝绿增强 | ⚠️ |
| Chrome | 类似 Kodachrome 反转片，浓郁色彩 | ❓ |
| I Model A | 1925 Ur-Leica，强颗粒、低对比、褪色暖调 | ⚠️ |

---

## 维度 B: Leica 代际色彩科学

### B.1 M 系列色彩演进表

| 代 | 传感器 | 核心特征 | 社区地位 |
|----|--------|---------|---------|
| **M8** (2006) | Kodak CCD 10MP APS-H | IR 问题严重，黑白优秀 | 过渡产品 |
| **M9** 🔥 (2009) | Kodak KAF-18500 CCD 18MP FF | 深幽蓝、油润翠绿、极高微对比/通透感 | 🌟 神话级 |
| **M240** (2012) | CMOSIS CMOS 24MP | 过饱和、偏黄绿、焦外浑浊 | ⚠️ 争议极大 |
| **M10** (2017) | CMOS 24MP→M10-R 40MP | 收敛、微偏青、接近 M9 | ⭐ 平衡最佳 |
| **M11** (2022) | BSI CMOS 60MP | 中性准确、数码味、毁誉参半 | 🔴 分化严重 |

### B.2 「Leica Look」六维画像（⚠️ 全为社区定性共识）

| 维度 | 描述 | 最典型机型 |
|------|------|-----------|
| ① 饱和度 | 中高饱和但不刺眼，非全局增强而是特定色系 | M9 CCD |
| ② 影调曲线 | 高微对比度（CCD 全局电荷转移 + 无 AA 滤镜）+ 暗部细节保持 | M9 CCD |
| ③ 色相偏移 | 蓝→深幽蓝/青蓝，绿→油润翠绿，红→饱满但不偏橙 | M9 CCD |
| ④ 分色调 | 暗部轻微偏暖，高光干净 | M9 CCD |
| ⑤ 白平衡 | M9: ~5500-6000K 偏暖不准确；M10: 偏冷约 5200-5500K | 各代不同 |
| ⑥ 肤色 | 自然不猪肝红，高饱和下保持肤色克制 | M9 最优 |

### B.3 CCD vs CMOS 物理差异推断

```
Kodak CCD 色彩独特性根源（⚠️ 推断）：
  ① CFA 分色特性不同（Kodak RGB 原色滤光片 vs Sony 现代 CFA）
  ② 无 AA 滤镜 → 天然高微对比度
  ③ 全局电荷转移 → 像素间一致性极高 → 图像「干净」
  ④ 盖板玻璃/微透镜/CFA 总成 → 光谱响应不同
```

---

## 维度 C: 逆向工程路径评估

### C.1 路径总览

| # | 路径 | 技术成熟度 | 所需资源 | 精度 | 优先级 |
|---|------|-----------|---------|------|--------|
| 1 | **Adobe DCP 提取** | ✅ 成熟（dcpTool） | Adobe CR/LR 安装 | ⭐⭐⭐-⭐⭐⭐⭐⭐ | 🥇 P1 |
| 2 | **小米徕卡跨平台参考** | ✅ 可行 | Xiaomi 17 Ultra 或评测样张 | ⭐⭐⭐ | 🥇 P0 |
| 3 | **Leica LUX App 逆向** | ❓ 待验证 | iPhone + LUX Pro 订阅 | ⭐⭐⭐⭐ | 🥈 P2 |
| 4 | **Flickr 直出样张统计** | ✅ 可行 | 网络搜索 | ⭐⭐ | P3 |
| 5 | **RAW+JPEG 配对标定**（Leica 相机） | 🔴 关键路径被封 | Leica Q3/SL3 | ⭐⭐⭐⭐⭐ | P4 |
| 6 | **社区预设反推** | ⭐ 低 | 购买商业预设 | ⭐⭐ | P5 |

### C.2 关键发现：机内 RAW 显影切换路径被封

**慧/正 确认：** Leica M 系列不支持类似 Ricoh GR 的「机内 RAW 显影时切换色彩模式」功能。这意味着无法通过一张 RAW → 多个风格导出 JPEG 获得完美像素对齐配对。

**影响：** 逆向精度最高（⭐⭐⭐⭐⭐）的 RAW+JPEG 配对法在 Leica 上无法实现，除非：
- 实际持有 Q3/SL3 并用不同 Film Style 各拍一张（但场景无法完全对齐）
- 通过小米手机实现（一张 RAW → Authentic/Vibrant JPEG 配对）

### C.3 立即可执行（无需 Leica 硬件）

1. ✅ 从 Adobe Camera Raw 目录提取 Leica DCP → dcpTool 反编译
2. ✅ 收集 Xiaomi 17 Ultra Leica 滤镜评测样张
3. ✅ 在 Flickr 搜索「Leica Q3 Standard JPEG」「Leica M9 直出」
4. 安装 Leica LUX App（免费版）→ 用测试图输入，截取各 Look 输出

---

## 维度 D: 引擎适配评估

### D.1 引擎参数覆盖度矩阵

| Leica 色彩特征 | 引擎可表达？ | 备注 |
|---------------|------------|------|
| 中高饱和度 | ✅ global_saturation | — |
| 蓝色深度/偏移 | ✅ blue_sat/lum/hue | M9 CCD 蓝→青蓝 |
| 中高微对比度 | ✅ tone.contrast + per_channel | — |
| 暗部细节保持 | ✅ shadow_toe_power + black_lift | — |
| 暖调白平衡偏移 | ✅ white_balance_shift_k | — |
| 肤色保护 | ✅ skin_hue/sat | — |
| 分色调 | ✅ shadow_tint / highlight_tint | — |
| **暗角** | ❌ | 需要新增 vignette_strength |
| **逐通道饱和度** | ❌ | 当前仅全局+蓝色特殊处理 |
| **绿色通道亮度增强** | ❌ | M9 CCD 翠绿需绿色 luma boost |
| **高光滚降形状** | ⚠️ | 当前仅有 power 参数，不够精细 |
| **3D 感/微对比度（空间域）** | ❌ | CCD 像素级一致性超出纯色调引擎范围 |

**覆盖度估计：约 60-70%**

### D.2 可能需要扩展的引擎参数

1. `vignette_strength` — 暗角强度
2. `green_luminance_boost` — 绿色通道亮度（M9 CCD 翠绿）
3. `per_channel_saturation [R, G, B]` — 逐通道饱和度（红色克制+蓝色增强）
4. `highlight_rolloff_shape` — 高光滚降形状（当前仅 power 不够）

---

## 维度 E: 与现有预设的区分度

| 维度 | HNCS | Gold 200 | 5219 | Positive Film | **M9 CCD Leica** |
|------|------|----------|------|---------------|-----------------|
| 设计哲学 | 自然优于准确 | 胶片 nostalgia | 电影戏剧 | 反转片鲜活 | **CCD 数码「胶片味」** |
| 饱和度 | 1.00 | 1.12 | 0.90 | 1.15-1.20 | **1.05-1.15·深沉** |
| 蓝色 | 自然深度 | 偏暖 | 默认 | 深度增青 | 🔥 **深幽蓝·油润** |
| 绿色 | 自然 | 偏黄 | 默认 | 中性偏浓 | 🔥 **油润翠绿** |
| WB | -250K | +400K | 中性 | +300K | **+400-800K** |
| 微对比 | 中灰增强 | 柔和 | 柔和 | 清晰锐利 | 🔥 **极高·焦外通透** |

**结论：M9 CCD Leica Look 在现有预设空间中完全独特，不重叠。**

---

## 维度 F: 第一优先级复刻目标

| 优先级 | 目标 | 理由 |
|--------|------|------|
| ⭐ **P0** | **Leica Classic Look**（Leica LUX + 小米 Authentic）+ **M9 CCD Look** | 适用范围最广 + 社区辨识度最高 |
| ⭐ **P1** | **M10 Look** | 「平衡最佳」代表现代方向 |
| P2 | Leica Chrome Look | 最新加入、越来越多讨论 |
| P3 | M11 Look | 最新代但争议大 |

---

## 已识别跨报告矛盾

| # | 矛盾 | 解决 | 
|---|------|------|
| 1 | 慧: Leica Looks「不可调」 vs 源: FW4.0.0 起可调强度 | → 源更准确（FW更新） |
| 2 | 慧: M11 可能无 Film Style 菜单 vs 明: 未直接验证 | → 需确认 |
| 3 | 慧: ~5 Film Styles vs 源: 5 确认 | → 一致 |
| 4 | FOTOS Looks 完整名单: 慧 未确证 vs 源 推断 7 个 | → 实际相机/固件日志验证前不能确认 |

---

## 缺口总览

### 🔴 高严重度

| # | 缺口 | 
|---|------|
| 1 | Leica Adobe DCP Profile 类型未知（Adobe Standard only 或包含 Camera Matching？） |
| 2 | 所有 Film Styles 和 Looks 的色彩特征无官方文档，全为推断 |
| 3 | Film Style 的可调参数精确范围未确认 |
| 4 | M9 CCD 色彩特征无量化数据 |
| 5 | Leica 相机不支持机内 RAW 显影切换 → 最佳逆向路径被封 |

### 🟡 中严重度

| # | 缺口 |
|---|------|
| 6 | FOTOS 相机版 7 种 Leica Looks 的完整官方清单缺失 |
| 7 | LUX Pro 11 种 Looks 中 4 种名称未知 |
| 8 | Leica 社区不存在集中式配方数据库 |
| 9 | Xiaomi 17 Ultra 9 滤镜完整命名列表 |
| 10 | M11 是否有 Film Style 菜单未确认 |

### 🟢 低严重度

| # | 缺口 |
|---|------|
| 11 | Leica Blue 是否存在 |
| 12 | 固件版本间 Film Style 微调历史 |
| 13 | 华为 P 系列 Leica 合作色彩配置 |
| 14 | L² 技术对 SL 系列色彩的影响 |

---

## 主要来源索引

| 来源 | URL | 可信度 |
|------|-----|--------|
| Leica LUX 官网 | leica-camera.com/en-US/photography/leica-apps/leica-lux | ✅ 官方 |
| Leica SL3 新闻稿 | leica-camera.com/en-US/press/new-leica-sl3 | ✅ 官方 |
| Leica SL3-S 产品页 | leica-camera.com/en-US/photography/cameras/sl/sl3-s-black | ✅ 官方 |
| dcpTool SourceForge | sourceforge.net/projects/dcptool/ | ✅ 开源 |
| dcpTool 教程（博客园） | cnblogs.com/nemuzuki/p/18159016 | ✅ 实测 |
| DPReview Q3 43（东方摄影翻译） | ea360.com/contents/226/25188.html | ⚠️ 二手 |
| DCFever Q3 43 | dcfever.com/news/readnews.php?id=38326 | ✅ 媒体 |
| 中关村在线 — 小米徕卡双画质 | dcdv.zol.com.cn/1002/10025154.html | ✅ 官方 PM |
| 今日头条 — 小米 17 Ultra 9 滤镜 | toutiao.com/article/7631469612605817378/ | ⚠️ 自媒体 |
| Sohu CCD vs CMOS 君峰 | sohu.com/a/124200997_417563 | ⚠️ 社区 |
| Chiphell M9/M10/M11 长测 | chiphell.com 多篇 | ⚠️ 用户评测 |
| DxOMark Leica M10 | dxomark.com/Cameras/Leica/M10 | ✅ 专业 |
| IT之家 FOTOS 4.0 | ithome.com/0/696/142.htm | ✅ 媒体 |
| IT之家 FW 4.0.0 | ithome.com/0/906/169.htm | ✅ 媒体 |

---

## Round 2 补充发现

### R2.1 已解决的跨报告矛盾

| # | 矛盾 | Round 2 结果 |
|---|------|-------------|
| 1 | Leica Looks 是否可调 | ✅ **已解决**：FW <4.0.0 固定预设，FW 4.0.0+ **全局强度 slider**，各参数不可单独调 |
| 2 | M11 是否有 Film Style 菜单 | ❓ **仍未确认**：搜索未找到明确证据，需要 M11 手册或持有者验证 |
| 3 | FOTOS Looks 完整名单 | ⚠️ **部分确认**：Chrome 确认为第 7 个（Q3 43 首发），其余 6 个仍为推断 |

### R2.2 关键新发现

1. 🔴 **Leica 官方文档极其稀疏**：针对 "Leica Q3 manual film style contrast saturation"、"Leica SL3 manual JPEG settings" 的多次搜索均返回非 Leica 内容或完全无关结果。这与 Ricoh GR 研究形成鲜明对比——理光有完整的中日英三种语言的 Image Control 说明页面。**Leica 对机内色彩配置的文档透明度在主流品牌中属于最低水平。**

2. 🔴 **DPReview 被 Cloudflare 屏蔽**：DPReview 的样张画廊和 studio scene 工具无法通过 WebFetch 访问。这意味着自动化下载 Leica 样张的工作流受阻，需要手动浏览器访问。

3. ✅ **Leica Chrome 确认**：DCFever 2024-09-26 报道 Q3 43 发布时明确写「新增多一项 Leica Chrome 滤镜」→ Chrome 是第 7 个 Leica Look，**相机独占**（LUX App 中未出现）。

4. ❓ **Panasonic Photo Style 参数体系**：多次搜索未找到 S5II/S1R 的完整 Photo Style 参数列表。Panasonic 在此方面同样存在文档不足的问题。

### R2.3 Round 2 未解决的缺口（从 Verifier 审计继承）

| # | 缺口 | 现状 |
|---|------|------|
| 1 | Leica Q3/SL3 用户手册 PDF 中 Film Style 精确参数范围 | 🔴 手册内容未能在搜索引擎中被索引 |
| 2 | Adobe DCP 目录中 Leica 文件的实际存在性 | 🔴 需要在有 Adobe LR/CR 的电脑上手动执行 `ls` + dcpTool 验证 |
| 3 | DPReview 在线 DNG 样张下载 | 🔴 Cloudflare 屏蔽，需要手动浏览器访问 |
| 4 | Panasonic S5II Photo Style 完整参数表 | 🟡 搜索结果一直返回产品购买页而非技术文档 |
| 5 | Leica M9/M11 JPEG 色彩特征量化数据 | 🔴 全为定性描述 |
| 6 | Leica Looks 各风格的视觉对比样本 | 🟡 L-Camera-Forum 存在讨论但未被搜索引擎充分索引 |

### R2.4 无相机可执行的下一步（优先级排序）

鉴于 Round 2 搜索确认了公开文档的稀疏性，以下操作需要用户手动执行：

| 优先级 | 操作 | 预计耗时 | 收益 |
|--------|------|---------|------|
| 🔴 P0 | 在有 Adobe LR/CR 的机器上 `ls ~/Library/Application Support/Adobe/CameraRaw/CameraProfiles/Camera/ \| grep -i leica` 并用 dcpTool 反编译 | 10 分钟 | ⭐⭐⭐⭐⭐ 最高信息密度 |
| 🔴 P0 | 从 Leica 官网下载 Q3 + SL3 用户手册 PDF，查阅 Film Style 章节 | 5 分钟 | ⭐⭐⭐⭐ |
| 🟡 P1 | 浏览器访问 DPReview Leica M11/Q3/SL3 sample gallery 下载 DNG+JPEG 样张 | 30 分钟 | ⭐⭐⭐⭐ |
| 🟡 P1 | 安装 Leica LUX App（免费版），用纯色测试图输入，截取各 Look 输出 | 1 小时 | ⭐⭐⭐⭐ |
| 🟢 P2 | 浏览器访问 L-Camera-Forum 搜索 Leica Looks 对比讨论 | 30 分钟 | ⭐⭐⭐ |
