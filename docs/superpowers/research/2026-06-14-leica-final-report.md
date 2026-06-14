# 徕卡色彩配置逆向工程 — 最终调研报告

**日期:** 2026-06-14
**状态:** 3 轮探索完成（R1→GAPS→R2→GAPS→R3→✅）→ Phase 4 最终交付
**核心问题:** 徕卡（Leica）有哪些适用范围广、社区辨识度高的色彩配置？可行的逆向工程路径有哪些？

---

## 执行摘要

**徕卡的色彩配置体系分为三层：①机内 Film Styles（5 种，可调参数 ~3 个）②FOTOS 下载 Leica Looks（7 种固定预设，FW4.0.0 起可调全局强度）③Leica LUX App Looks（11 种）。**

**第一优先级复刻目标为 Leica Classic Look（适用范围最广）和 M9 CCD Look（社区辨识度最高）。**

**🔴 最关键的发现：Adobe 对 M9/M10/M11/Q3/SL3 等主力徕卡机型的 Camera Matching = No（本地 DCP 目录验证 + Adobe 官方页面双重确认）。这意味着从 Adobe DCP 中提取风格化色彩数据（3D LUT/ProfileLookTable）的路径被封死**，仅能提取传感器基线矩阵。这与 Ricoh GR III 的 DCP 路径（Camera Matching = Yes → 可直接获取 Positive Film 色彩变换）形成根本性差异。

逆转策略重新排序后最佳无相机路径为：**小米徕卡跨平台参照 → Leica LUX App 逆向 → DPReview/PhotographyBlog DNG 样本分析 → Panasonic S5M2 Camera Matching profiles（代理数据）**。

**引擎可覆盖约 60-70% 的 Leica 色彩特征。** M9 CCD 的蓝绿色彩特征 + 通透感在现有预设空间（HNCS / Gold 200 / 5219 / Positive Film）中**完全独特、不重叠**。

---

## 1. 徕卡色彩配置体系全景

### 1.1 三层架构（✅ 多源交叉确认）

```
Leica 色彩配置体系
├── ① 机内 Film Styles（内置·可调参数 ~3 个）
│   ├── Standard / Vivid / Natural / Monochrome / HC B&W
│   ├── 可调: Contrast, Saturation, Sharpening（确切范围未确认，推测 ±3~±5）
│   └── 覆盖: Q3/Q3 43/SL3（M 系列旁轴不支持 Film Style 选择 ❓待确认）
│
├── ② Leica Looks（FOTOS App 下载·7 种·FW4.0.0 起可调强度）
│   ├── Classic, Contemporary, Vivid, B&W, Eternal, Selenium, Chrome
│   ├── FW<4.0.0: 固定预设；FW≥4.0.0: 全局强度 slider（非各参数独立可调）
│   └── 仅支持: Q3/Q3 43/SL3/SL3-S
│
└── ③ Leica LUX App Looks（iPhone·11 种·Pro 付费）
    ├── 免费: 5 种色彩模式（同 Film Styles）
    ├── Pro: Classic, Contemporary, Vivid, B&W, Eternal, Selenium, I Model A + 4 未知
    └── Artist Look: Greg Williams
```

### 1.2 与 Ricoh GR Image Control 对比

| 维度 | Ricoh GR III | Leica Q3/SL3 |
|------|-------------|-------------|
| 风格数 | 12（彩色8+黑白4） | 5+7=12（Film Styles 5 + Looks 7） |
| 可调参数数 | **14** | **~3** |
| 正片/负片 | ✅ Positive Film, Negative Film | ❌ |
| 社区配方生态 | ✅ ricohrecipes.com 38+ 配方 | ❌ 不存在集中式配方社区 |
| 官方文档透明度 | ✅ 官方表现力页面 | ❌ 文档极少（搜索引擎中几乎不可索引） |
| Adobe Camera Matching | ✅ Camera Matching = Yes（6 个 GR 风格） | **🔴 Camera Matching = No**（仅 M8、V-LUX 5 例外） |

---

## 2. 代际色彩特征

### 2.1 M 系列色彩演进

| 代 | 传感器 | 核心特征 | 社区地位 |
|----|--------|---------|---------|
| **M9** 🔥 (2009) | Kodak KAF-18500 CCD 18MP FF | 深幽蓝、油润翠绿、极高微对比/通透感 | 🌟 神话级 |
| **M240** (2012) | CMOSIS CMOS 24MP | 过饱和、偏黄绿 | ⚠️ 争议极大 |
| **M10** (2017) | CMOS 24→40MP | 收敛、微偏青、接近 M9 | ⭐ 平衡最佳 |
| **M11** (2022) | BSI CMOS 60MP | 中性准确、偏数码味 | 🔴 毁誉参半 |

### 2.2 「Leica Look」六维画像（⚠️ 社区定性共识，未量化）

| 维度 | 描述 | 最典型 |
|------|------|--------|
| ① 饱和度 | 中高饱和但不刺眼，特定色系增强（非全局） | M9 CCD |
| ② 影调 | 高微对比度 + 暗部细节保持。CCD 自带像素级一致性→焦外通透「清汤」 | M9 CCD |
| ③ 色相 | 蓝→深幽蓝/青蓝，绿→油润翠绿，红→饱满不偏橙 | M9 CCD |
| ④ 分色调 | 暗部微暖，高光干净 | M9 CCD |
| ⑤ 白平衡 | M9: ~5500-6000K 偏暖；M10: ~5200-5500K 微冷；M11: 中性 | 各代不同 |
| ⑥ 肤色 | 自然不猪肝红，高饱和下保持克制 | M9 最优 |

### 2.3 CCD vs CMOS 物理差异推断

```
M9 CCD 色彩独特性根源（⚠️ 推断）：
  ① Kodak KAF-18500 CFA 分色特性 → 原色信号纯度更高
  ② 无 AA 滤镜 → 天然高微对比度
  ③ 全局电荷转移 → 像素间一致性极高→图像「干净」 vs CMOS 每像素独立放大器→「浑浊」
  ④ 盖板玻璃/微透镜/CFA 总成光谱响应不同于现代 Sony CMOS
```

---

## 3. 🔴 逆向工程路径评估（已修正）

### 3.1 路径总览

| # | 路径 | 技术成熟度 | 所需资源 | 精度 | 优先级 | 状态 |
|---|------|-----------|---------|------|--------|------|
| 1 | ~~Adobe DCP 风格提取~~ | ✅ 但 Leica Camera Matching=No | Adobe LR/CR | ~~⭐⭐⭐⭐~~→⭐ | ~~P0~~→P4 | 🔴 **已降级** |
| 2 | **小米徕卡跨平台参照** | ✅ 可行 | Xiaomi 17 Ultra / 评测样张 | ⭐⭐⭐ | 🥇 **P0** | ✅ 可行 |
| 3 | **Leica LUX App 逆向** | ❓ 待验证 | iPhone + LUX Pro | ⭐⭐⭐⭐ | 🥈 **P1** | 待执行 |
| 4 | **DPReview/PhotographyBlog DNG 样张** | ✅ 可行 | 浏览器手动下载 | ⭐⭐⭐ | 🥉 **P2** | 需绕过 Cloudflare |
| 5 | Panasonic S5M2 Camera Matching（代理） | ✅ 本地已有 | dcpTool/自制解析器 | ⭐⭐⭐ | P3 | ✅ 可立即执行 |
| 6 | RAW+JPEG 配对标定（Leica 相机） | 🔴 路径被封 | Leica Q3/SL3 | ⭐⭐⭐⭐⭐ | P4 | ❌ M 系列不支持机内 RAW 显影切换 |

### 3.2 🔥 关键发现：Adobe Camera Matching = No

**从 Adobe 官方相机支持页面（https://helpx.adobe.com/camera-raw/kb/camera-raw-plug-supported-cameras.html）提取的数据：**

| 仅有例外 | Camera Matching |
|---------|----------------|
| **Leica M8** | ✅ **Yes** |
| **Leica V-LUX 5** | ✅ **Yes** |
| **所有其他机型**（M9/M10/M11/M240/Q/Q2/Q3/SL/SL2/SL3/S 等 ~40 台） | ❌ **No** |

**本地验证（通过用户 Mac 上的 Adobe Lightroom Classic 安装目录）：**
- Lightroom 内嵌的 `CameraProfiles/Camera/` 目录确认：仅有 Leica M8、V-Lux 5、D-Lux 7、C-Lux 的 Camera Matching profiles
- 这些 Camera Matching profiles 的 ColorMatrix1/2 在所有 Style（Standard/Vivid/Natural 等）之间完全相同，风格差异可能编码在 ProfileLookTable 中
- M9/M10/M11/Q3/SL3 在 `Adobe Standard/` 目录中仅有 Adobe Standard profile（传感器基线变换，不含风格化数据）

**Panasonic DC-S5M2 代理数据（本地已有）：**
- 完整的 17 个 Camera Matching profiles，包括 Leica 联名风格：
  - `L Monochrome`, `L Monochrome D`, `L Monochrome S`（Leica 黑白风格）
  - `L Classic Neo`（Leica 经典风格）
  - `Cinelike D2`, `Cinelike V2`
  - Standard, Vivid, Natural, Flat, Landscape, Portrait, Monochrome
- **SL 系列与 Panasonic S 系列共享 L² 技术 + L-Mount 标准** → S5M2 的 Camera Matching profiles 是最接近 SL3 Leica Looks 的可分析代理数据

### 3.3 立即可执行（无需 Leica 硬件）

| 优先级 | 操作 | 预计耗时 | 收益 |
|--------|------|---------|------|
| 🔴 P0 | 搜索 Xiaomi 17 Ultra Leica 滤镜评测样张 → 下载 JPEG 样本 | 30 分钟 | ⭐⭐⭐ |
| 🔴 P0 | 安装 dcpTool → 反编译 Panasonic S5M2 Camera Matching profiles → 提取 LUT | 15 分钟 | ⭐⭐⭐⭐ |
| 🟡 P1 | 安装 Leica LUX App（免费版），用纯色测试图输入，截取各 Look 输出 | 1 小时 | ⭐⭐⭐⭐ |
| 🟡 P1 | 浏览器下载 DPReview Leica M11/Q3 sample gallery DNG | 30 分钟 | ⭐⭐⭐ |
| 🟢 P2 | rawpy 解析 DNG → 提取 ColorMatrix 标签 → 获得传感器基线色彩矩阵 | 30 分钟 | ⭐⭐⭐ |
| 🟢 P2 | L-Camera-Forum / Reddit 搜索 Leica Looks 视觉对比讨论 | 30 分钟 | ⭐⭐ |

---

## 4. 引擎适配评估

### 4.1 参数覆盖度矩阵

| Leica 色彩特征 | 引擎可表达？ | 备注 |
|---------------|------------|------|
| 中高饱和度 | ✅ `global_saturation` | — |
| 蓝色深度/偏移 | ✅ `blue_sat/lum/hue` | M9 CCD 蓝→青蓝 |
| 中高对比度 | ✅ `tone.contrast` + `per_channel_contrast` | — |
| 暗部细节保持 | ✅ `shadow_toe_power` + `black_lift` | — |
| 暖调白平衡 | ✅ `white_balance_shift_k` | — |
| 肤色保护 | ✅ `skin_hue_min/max` + `skin_sat_adjust` | — |
| 分色调 | ✅ `shadow_tint` / `highlight_tint` | — |
| **暗角** | ❌ | 需新增 `vignette_strength` |
| **逐通道饱和度** | ❌ | 当前仅全局+蓝色特殊处理，需 `per_channel_saturation [R,G,B]` |
| **绿色亮度增强** | ❌ | M9 CCD 翠绿需 `green_luminance_boost` |
| **高光滚降形状** | ⚠️ | 当前仅有 `highlight_shoulder_power`，不够精细 |
| **微对比度/3D 感（空间域）** | ❌ | CCD 像素级一致性超出纯色调引擎范围 |

**覆盖度估计：约 60-70%**

### 4.2 建议新增的引擎参数

```python
# 建议在 engine/core.py apply_color_grade() 中新增:
'vignette_strength': 0.0,          # 暗角强度（0.0=无, 1.0=全黑边缘）
'green_luminance_boost': 0.0,      # 绿色通道亮度偏移（正值=更亮/油润）
'per_channel_saturation': [1.0, 1.0, 1.0],  # [R, G, B] 逐通道饱和度乘数
'highlight_rolloff_shape': 1.0,    # 高光滚降形状（替代单一 power 参数）
```

---

## 5. 与现有预设的区分度

| 维度 | HNCS | Gold 200 | 5219 | Positive Film | **M9 CCD Leica** |
|------|------|----------|------|---------------|-----------------|
| 设计哲学 | 自然优于准确 | 胶片 nostalgia | 电影戏剧 | 反转片鲜活 | **CCD 数码「胶片味」** |
| 饱和度 | 1.00 | 1.12 | 0.90 | 1.15-1.20 | **1.05-1.15·深沉** |
| 蓝色 | 自然深度 | 偏暖 0.95 | 默认 | 深度增青 1.10-1.20 | 🔥 **深幽蓝·油润** |
| 绿色 | 自然 | 偏黄 | 默认 | 中性偏浓 | 🔥 **油润翠绿** |
| WB 偏移 | -250K | +400K | 中性 | +300K | **+400-800K** |
| 微对比 | 中灰增强 | 柔和 | 柔和 | 清晰锐利 | 🔥 **极高·焦外通透** |

**结论：M9 CCD Leica Look 在现有预设空间中完全独特，不重叠。**

---

## 6. 第一优先级复刻目标

| 优先级 | 目标 | 理由 | 可行性 |
|--------|------|------|--------|
| ⭐ **P0** | **Leica Classic Look** | 适用范围最广（LUX app + FOTOS + 小米三重对应） | 小米样张可获取 + LUX app 可测试 |
| ⭐ **P0** | **M9 CCD Look** | 社区辨识度最高（神话级），与现有预设完全不重叠 | 最难（需 M9 相机做精确标定），但社区样张可做初始猜测 |
| P1 | M10 Look | 「平衡最佳」代表现代方向 | 样张可获取 |
| P2 | Leica Chrome Look | 最新加入，讨论度上升 | 样张极少 |
| P3 | M11 Look | 最新代但争议大、定义不稳定 | 样张可获取 |

---

## 7. 缺口与后续行动

### 7.1 🔴 高优先级缺口

| # | 缺口 | 解决方式 |
|---|------|---------|
| 1 | M9 CCD 色彩无量化数据 | 需要 M9 相机 + ColorChecker 标定拍摄（长期） |
| 2 | Film Style 精确参数范围和默认值未确认 | 需要 Q3/SL3 用户手册（Leica 官网有 PDF 下载） |
| 3 | Leica Looks 各风格实际视觉差异未验证 | 需要实际 Q3/SL3 + FOTOS app 或 LUX app 测试 |
| 4 | M11 是否完全没有 Film Style 菜单 | 需 M11 用户确认或手册查阅 |
| 5 | Panasonic S5M2 Camera Matching LUT 数据未提取 | 需安装 dcpTool 或完善自制解析器 |

### 7.2 🟡 中优先级缺口

| # | 缺口 |
|---|------|
| 6 | FOTOS Looks 与 LUX Looks 是否一一对应 |
| 7 | Leica Looks 色彩特征全为名称推断，无实测支撑 |
| 8 | Xiaomi 17 Ultra 9 滤镜完整命名列表 |
| 9 | L² 技术对 SL 系列色彩的具体影响程度 |
| 10 | Leica JPEG EXIF MakerNote 是否包含 Film Style 标签 |

### 7.3 🟢 低优先级缺口

| # | 缺口 |
|---|------|
| 11 | Leica Blue Look 是否存在 |
| 12 | 固件版本间 Film Style 微调历史 |
| 13 | Leica SL/SL2 旧代色彩特征 |
| 14 | Leica CL/TL/S 系列色彩配置 |

---

## 8. 主要参考文献

| 来源 | URL | 可信度 |
|------|-----|--------|
| Leica LUX App 官网 | https://leica-camera.com/en-US/photography/leica-apps/leica-lux | ✅ 官方 |
| Leica SL3 新闻稿 | https://leica-camera.com/en-US/press/new-leica-sl3 | ✅ 官方 |
| Leica SL3-S 产品页 | https://leica-camera.com/en-US/photography/cameras/sl/sl3-s-black | ✅ 官方 |
| Adobe 相机支持列表 | https://helpx.adobe.com/camera-raw/kb/camera-raw-plug-supported-cameras.html | ✅ 官方 |
| dcpTool SourceForge | https://sourceforge.net/projects/dcptool/ | ✅ 开源 |
| 小米徕卡双画质（中关村在线） | https://dcdv.zol.com.cn/1002/10025154.html | ✅ 官方 PM |
| DPReview Q3 43 评测（东方摄影翻译） | https://www.ea360.com/contents/226/25188.html | ⚠️ 二手翻译 |
| DCFever Q3 43 | https://www.dcfever.com/news/readnews.php?id=38326 | ✅ 媒体 |
| IT之家 FOTOS 4.0 | https://www.ithome.com/0/696/142.htm | ✅ 媒体 |
| IT之家 FW 4.0.0 | https://www.ithome.com/0/906/169.htm | ✅ 媒体 |
| Sohu CCD vs CMOS | https://www.sohu.com/a/124200997_417563 | ⚠️ 社区 |
| Chiphell M9/M10/M11 长测 | chiphell.com 多篇 | ⚠️ 用户评测 |
| DxOMark Leica M9 | https://www.dxomark.com/Cameras/Leica/M9 | ✅ 专业 |
| DxOMark Leica M10 | https://www.dxomark.com/Cameras/Leica/M10 | ✅ 专业 |
| 色影无忌 Q3 DR | https://info.xitek.com/news/202311/08-365573.html | ✅ 专业 |
| smzdm M9 vs M240 实拍 | https://post.smzdm.com/talk/p/a7neg849/ | ⚠️ 用户实拍 |

---

## 9. 附录：本地 DCP 验证结果

### 9.1 已验证的 Leica Camera Matching Profiles（Adobe Lightroom Classic 内嵌）

| 机型 | Camera Matching | Styles（Vivid/Standard 等） | 备注 |
|------|----------------|---------------------------|------|
| Leica M8 | ✅ | Camera Standard（1 个） | — |
| Leica V-Lux 5 | ✅ | Standard, Vivid, Natural, Portrait, Scenery, Monochrome, Monochrome HC, Cinelike D, Cinelike V（9 个） | 本质为 Panasonic 换标 |
| Leica D-Lux 7 | ✅ | Standard, Vivid, Natural, Portrait, Scenery, Monochrome, Monochrome HC（7 个×v1+v2） | 本质为 Panasonic 换标 |
| Leica C-Lux | ✅ | Standard, Vivid, Natural, Portrait, Scenery, Monochrome, Monochrome HC（7 个） | 本质为 Panasonic 换标 |
| M9/M10/M11/Q3/SL3 | ❌ | 无 | 仅有 Adobe Standard |

### 9.2 Panasonic S5M2 Camera Matching Profiles（SL 系列代理数据）

已确认 17 个 Camera Matching profiles，包含 Leica 联名风格：
- **L Monochrome / L Monochrome D / L Monochrome S** — Leica 黑白风格
- **L Classic Neo** — Leica 经典现代
- Cinelike D2 / Cinelike V2 — 电影风格
- Standard / Vivid / Natural / Flat / Landscape / Portrait / Monochrome — 基础风格
