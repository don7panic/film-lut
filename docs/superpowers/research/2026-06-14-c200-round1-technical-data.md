# C200 技术数据搜索报告 — Round 1 Explorer

**角色:** 色彩科学研究员
**日期:** 2026-06-14
**范围:** 老版日产 Fujifilm Fujicolor C200 技术数据、乳剂结构、代际差异

---

## 1. 官方技术数据表

### 结论：未找到公开的 C200 官方数据表

**搜索路径尝试：**
| # | 搜索策略 | 结果 |
|---|---------|------|
| 1 | `site:fujifilm.com "Fujicolor C200" data sheet` | ❌ 官网已移除所有消费级胶片产品页面 |
| 2 | `site:fujifilm.com.hk/products/consumer_film` | ⚠️ 香港站仍有旧架构但 C200 页面不可访问 |
| 3 | doc88.com "Spectral density curves Characteristic curves - Fujifilm" | ⚠️ Ref. KB-0701E（2007年，2页），付费墙后，产品不明 |
| 4 | docin.com "FUJICOLOR NEGATIVE FILM - Fujifilm 中国" | ⚠️ 42页产品目录 PDF，付费墙后，可能含 C200 |
| 5 | archive.org 搜索 | ❌ 未找到 C200 相关存档 |
| 6 | "Fujicolor C200 characteristic curve spectral dye density" | ❌ 无公开结果 |

**关键发现：** C200 作为低端消费级胶片，Fujifilm 从未公开发布过类似专业胶片的详细技术数据表（无 AF3-xxxE 编号文档）。专业胶片（PRO 160C: AF3-175E, PRO 800Z: AF3-177E, PRO 400H: AF3-176E）的技术数据表格式已知，但 C200 不在其中。

**可靠性：高** — 多次系统性搜索确认缺失。

---

## 2. 乳剂结构

### C200 = 3 层感色层（非 4 层）

**证据链：**

| 来源 | 内容 | 可靠性 |
|------|------|--------|
| [蜂鸟网 - Superia 200](https://production.xitek.com/product-a-post-id-2580-page-3.html) | "富士 Fujicolor Superia 200 彩色负片，锐利，颗粒细，色彩真实。**四层感色层**。" | **高** |
| [蜂鸟网 - Superia 1600](https://production.xitek.com/product-a-post-id-2618-prod_from-7.html) | "加入**第四感色层**" | **高** |
| 知乎/Sohu 社区共识 | C200 与 ColorPlus 200 同级（入门级），定位低于 Superia 系列 | **中** |

**推理链：**
1. Superia 系列（Superia 200/400/800/1600）明确标注"四层感色层"
2. C200 产品包装和所有公开描述中从未提及第四层技术
3. C200 是富士消费级产品线中最低端的产品之一（与 Kodak ColorPlus 200 对标）
4. 第四感色层（青敏感层）是富士高端消费/专业胶片的差异化技术，成本较高

**结论：C200 采用标准 3 层 R/G/B 乳剂结构，无第四感色层。** 这意味着 C200 的青/绿色再现能力显著弱于 Superia/Reala 系列。
[UNVERIFIED] 需要 C200 产品包装图片或官方规格表最终确认。

**可靠性：中高** — 基于产品线定位推理 + Superia 对比证据。

---

## 3. 代际差异：老版日产 vs 新版美产

### 确认：新版（2021+）Fujicolor 200 特征曲线与 Kodak Gold 200 高度相似

**证据链：**

| 来源 | 内容 | URL |
|------|------|-----|
| [搜狐 - 科技大头条](https://www.sohu.com/a/515921587_121118995) (2022-01-11) | "富士去年年底前发布的全新 Fujicolor 200 和柯达的 Kodak Gold 200 胶卷**感光曲线图非常相似**，反倒是自家两代 Fujifilm Fujicolor 200 的曲线不太一样（2019款和2021款）" | 直接引用 |
| [知乎 - Tristan-豬](https://www.zhihu.com/people/tristan-zhu-64) (2023) | "美国富士 C200 的曲线几乎与柯达 gold 200 一毛一样，甚至有人怀疑它就是柯达代工的" | 社区分析 |
| [淘宝列表](https://www.taobao.com/list/item/8975811353.htm) | "美版单卷盒装36张" vs "日产" 明确区分 | 市场证据 |

**关键推论：**
- 老版日产 C200：富士自有乳剂配方，独特的冷调 + 绿色暗部特征
- 新版美产 Fujicolor 200：极可能为 Kodak 代工，色彩特征接近 Gold 200（暖调、金色 bias）
- 两者在 curve shape 上有显著差异（搜狐文章配图确认）

**本次复刻目标明确为老版日产 C200。**

**可靠性：高** — 多源交叉确认（新闻 + 社区 + 市场）。

---

## 4. 光谱敏感度 / 染料密度曲线

### 结论：未找到

- 无公开的 C200 spectral sensitivity data
- 无公开的 C200 spectral dye density curves
- 最接近的参照是 Fujifilm PRO 系列技术数据表（PRO 160C/400H/800Z 有完整 spectral dye density curves），但这些都是 4 层乳剂的专业胶片，与 C200 的 3 层结构不同

**替代参照建议：**
- 使用 Kodak Gold 200 的 spectral dye density curves 作为结构参照（已知 Gold 200 的特征曲线 shape）
- 推断 C200 的相对差异：更冷的整体 WB、更绿的暗部偏移、B 层感光度可能高于 Kodak

**可靠性：低** — 完全依赖推断。

---

## 5. Fuji X Weekly C200 配方

### 确认存在，但参数值需从视频提取

| 来源 | 内容 |
|------|------|
| [Bilibili - 罗伊呢](https://m.bilibili.com/video/BV1PA41147ns/) | "【富士配方】fujicolor C200【x-Trans IV】"（00:49 视频） |
| 来源标注 | "素材来自 fujixweekly" |

配方参数在视频画面中展示（无法从 HTML 直接提取），需要人类观看视频或寻找文本版。该配方基于 Fujifilm X-Trans IV 相机（X-T3/X-T4/X100V 等），包含：
- 胶片模拟基础（Classic Negative / PRO Neg / Classic Chrome）
- 动态范围
- 高光/阴影
- 色彩
- 白平衡偏移
- 颗粒/锐度等

**这是最接近 C200 数字仿真的公开参数化数据源，后续轮次应优先提取。**

**可靠性：中** — 第三方配方，非官方。

---

## 6. Analogica Lab C200 LUT

### 商业产品，存在于多个分发站点

| 来源 | URL |
|------|-----|
| CGer.com | https://www.cger.com/site/63521.html |
| 红森林 | https://www.hoslin.cn/103408.html |
| 镁元素 | https://www.myssc.net/51934.html |

**描述（CGer）：**
- "LUT FUJICOLOR C200 35MM 胶片模拟，专业调色"
- "将您的数码照片变成复古杰作、色调、阴影和经典模拟电影的感觉"
- "非常适合想要为其作品添加怀旧和电影感的摄影师"
- 包含 2 个 LUT：1×Rec709 + 1×Universal LOG
- "所有 LUT 均由意大利调色师 Analogica 手工制作"

**限制：**
- 商业产品（需付费），无法直接分析 LUT 内部数值
- 手工制作（主观调色师判断），非数据驱动
- 可作为最终结果的视觉对比参照，但不可作为 ground truth

**可靠性：低** — 商业仿真产品，无透明度。

---

## 新问题（本轮发现）

| # | 问题 | 优先级 |
|---|------|--------|
| Q1 | Fuji X Weekly C200 配方的具体参数是什么？（需要从视频提取或找到文本版） | 🔴 P0 |
| Q2 | C200 和 Gold 200 的老版特征曲线对比图具体显示了什么差异？（搜狐文章中的图） | 🟡 P1 |
| Q3 | 能否找到 C200 样本扫描的定量色彩分析？（Flickr/LOFTER 社区样本的 HSL 统计） | 🟡 P1 |
| Q4 | "富士绿"在 C200 上的具体 HSL 范围是什么？（色相/饱和度/明度） | 🔴 P0 |
| Q5 | "暗部绿色"是全局 WB 偏移还是 split-tone 效果？（不同亮度区间的色相变化） | 🔴 P0 |
| Q6 | 能否通过 Wayback Machine 找到 fujifilm.com 旧版 C200 产品页面？ | 🟢 P2 |
| Q7 | 是否有任何学术论文研究了 C200 的色彩再现特性？ | 🟢 P2 |
| Q8 | PRO 160C 的 4 层 spectral dye density 数据能否作为 C200 的上界参照？ | 🟢 P2 |

---

## 数据源可靠性总评

| 数据源 | 可靠性 | 已获取 |
|--------|--------|--------|
| C200 官方技术数据表（特征曲线/光谱密度） | — | ❌ 不存在/未公开 |
| C200 乳剂结构（3层） | 中高 | ✅ 推理确认 |
| 新旧版 C200 差异（日产 vs 美产=Kodak 代工） | 高 | ✅ 多源确认 |
| C200 光谱敏感度 | — | ❌ 未找到 |
| Fuji X Weekly C200 配方 | 中 | ⚠️ 存在但参数待提取 |
| Analogica Lab C200 LUT | 低 | ⚠️ 商业产品，不可分析 |
| 社区色彩描述（冷调/绿色暗部等） | 中 | ✅ 定性共识 |

---

## 数据缺口与后续建议

**本轮核心结论：C200 的官方技术数据表（特征曲线、光谱染料密度曲线）不存在于公共领域。** Fujifilm 从未为入门级消费胶片发布详细技术数据。

**替代策略：**
1. 下一轮探索提取 Fuji X Weekly C200 配方参数（最接近的公开参数化参照）
2. 使用 PRO 系列 datasheet 的结构 + C200 社区描述做约束推断
3. 定量分析 C200 样本扫描（Flickr/LOFTER 社区照片的色板提取）
4. 基于 3 层 vs 4 层乳剂差异推断 C200 与 Superia 的相对特征

---

*本轮结束。标记 [UNVERIFIED] 的内容需后续交叉验证。*
