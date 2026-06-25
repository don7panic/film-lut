# V-Log-Alchemy 对 AI Image-to-LUT 路线的启发

> 调研日期：2026-06-24  
> 本地项目：`/Users/oasis/workspace/V-Log-Alchemy`  
> GitHub remote：`https://github.com/shenmintao/V-Log-Alchemy.git`  
> 当前本地提交：`1073da4 fix: fix`  
> 许可证：Apache License 2.0

---

## 一、结论摘要

V-Log-Alchemy 对当前 `film-lut` 项目的最大启发不是代码复用，而是路线校准：它证明一条很实际的 LUT 生成路线是 **色彩空间伪装 + 成熟/官方 LUT 链式烘焙**，而不是只靠一组人工设计的 HSL/曲线参数去模拟所有 look。

这对 `AI 图片分析 -> LUT 自动生成` 的可行性判断有直接影响：

- 原报告中的 `VLM + CV + Optimization` 方向仍然合理。
- 但优化目标不应只来自单张参考图的统计分布。
- 更稳的路线是先建立 **style prototype registry**，让 AI/CV 做原型选择、强度估计和残差微调；第三方 LUT 文件不直接进入仓库。
- V-Log-Alchemy 可作为 prototype 来源、engine 表达能力 benchmark，以及真实 `.cube` 行为分析样本。

推荐把原报告中的 Phase 0 改为：先用 V-Log-Alchemy 的 LUT 做拟合 benchmark，判断当前参数化 engine 到底缺优化器、缺参数，还是缺更底层的色彩空间/3D 交叉通道表达能力。

---

## 二、V-Log-Alchemy 的核心路线

V-Log-Alchemy 是一个开源 GitHub 项目，仓库本身很轻，主要由预生成 `.cube` LUT、一个 DCTL 逆变换、README 和样片组成。它的目标是把 Panasonic Lumix 的 V-Log/V-Gamut 输入转换成 Fuji、Leica、ARRI、Nikon、RED、Cineon 等风格。

README 描述的核心流程是：

```text
Panasonic V-Log/V-Gamut
  -> ACES AP0 Linear
  -> 目标相机 IDT 逆运算
  -> 伪装成目标相机 Log/Gamut
  -> 应用目标厂商或成熟系统 LUT
  -> bake 成 Panasonic 可用 .cube
```

本地 DCTL `DCTL/ACES_to_FLog2C_Inverse.dctl` 展示了其中一个关键变换：把 ACES AP0 Linear 通过高精度逆矩阵和 F-Log2C 曲线编码，转换回 Fujifilm F-Gamut/F-Log2C。

这和当前 `film-lut` 的路线不同：

```text
当前 film-lut:
V-Log -> Rec.709 -> tone curve -> HSL/split-tone grade -> display gamma

V-Log-Alchemy:
V-Log -> ACES/目标 Log-Gamut -> 官方/成熟 LUT -> baked .cube
```

关键差异是：V-Log-Alchemy 不试图把所有风格还原成几个可解释参数，而是借用成熟色彩系统的完整 LUT 作为目标外观。

---

## 三、本地项目观察

### 3.1 资产结构

本地仓库包含：

| 类型 | 内容 |
|------|------|
| LUT | 23 个 33 点 `.cube`，分布在 `Luts/Fujifilm`, `Luts/Leica`, `Luts/Arri`, `Luts/Cineon`, `Luts/Nikon`, `Luts/RED` |
| DCTL | `DCTL/ACES_to_FLog2C_Inverse.dctl` |
| 样片 | `Samples/FujiFilm_Classic_Neg._Sample.jpg`, `Samples/Leica_Classic_Sample.jpg` |
| 文档 | `README.md`, `README_zh-CN.md` |
| 许可证 | Apache License 2.0 |

所有 `.cube` 的共同特征：

- `LUT_3D_SIZE 33`
- 带 `#LUMIXPHOTOSTYLE VLOG`
- 未显式写 `DOMAIN_MIN` / `DOMAIN_MAX`
- 面向 Panasonic V-Log/V-Gamut 输入

### 3.2 风格覆盖

代表性 LUT 包括：

| 类别 | 示例 |
|------|------|
| Fujifilm | Classic Neg, Classic Chrome, Provia, Velvia, Astia, Eterna, Eterna Bleach Bypass, Reala Ace, Acros |
| Leica | Classic, Natural |
| ARRI | LogC2Video Classic 709 |
| Cineon / Print Film | Kodak 2383, Fuji 3513DI |
| Nikon / RED | N-Log to Rec.709, RED FilmBias, RED Achromic, RED IPP2 Medium Contrast Soft |

这些 look 正好覆盖用户常见的“想要某种相机/胶片味道”的表达方式，比单纯从参考图里抽统计特征更贴近实际产品入口。

### 3.3 LUT 行为特征

抽样观察显示，V-Log-Alchemy 的 LUT 风格较硬，很多高饱和或纯色输入会把通道推到 0 或 1。这说明它追求 baked look 和相机/官方 LUT 的效果，而不是温和、可逆、可解释的调参模型。

因此它适合做：

- 原型库
- benchmark ground truth
- 竞品/开源参考
- 用户可选 look catalog

但不适合直接替代当前 engine 的参数化配方系统。

---

## 四、对原可行性报告的修正

原报告结论是：`VLM（语义） + CV（统计） + Optimization（数值优化）` 是推荐路线。这个方向依然成立，但 V-Log-Alchemy 暴露出一个重要缺口：**优化目标不应该只来自单张参考图的统计分布**。

### 4.1 原 A4 架构的问题

原报告设想：

```text
reference image -> CV statistics
neutral image -> LUT(params) -> statistics
optimize statistics distance
```

这个设计的问题是：单张 reference 的统计分布混合了场景内容和调色风格。例如蓝天、森林、夕阳、霓虹都会严重影响色相/饱和度直方图。VLM 能缓解，但不能保证稳定分离内容与风格。

### 4.2 更稳的改法

引入 prototype LUT 后，流程可以改为：

```text
reference image
  -> VLM/CV 判断风格原型
  -> 从 prototype LUT library 选 Top-K
  -> 估计强度、白平衡、对比、饱和、局部偏移
  -> 优化参数化 engine 或 residual LUT
  -> 输出 .cube + 可解释参数
```

这里的 AI 角色从“发明 LUT”变成：

- 识别 reference 接近哪个风格族
- 判断哪些颜色来自场景内容，哪些更像调色
- 给优化器提供 Top-K 原型和约束
- 解释生成结果

这样可以降低 VLM 数值不准和 CV 内容偏差带来的风险。

---

## 五、建议的 Phase 0 实验

建议在继续扩展 engine 前，先做一个小而硬的 benchmark。

### 5.1 目标

判断当前 `film-lut` 参数化 engine 对真实/成熟 LUT 的表达能力。

### 5.2 数据

使用 V-Log-Alchemy 的 23 个 `.cube` 作为 ground truth，优先选择：

- `Fujifilm/FLog2C_to_CLASSIC-Neg_VLog.cube`
- `Fujifilm/FLog2C_to_ETERNA_VLog.cube`
- `Fujifilm/FLog2C_to_CLASSIC-CHROME_VLog.cube`
- `Leica/L-Log_to_Classic_VLog.cube`
- `Cineon/Cineon_to_Kodak_2383_D65_VLog.cube`
- `Arri/ARRI_LogC2Video_Classic709_VLog.cube`

### 5.3 方法

1. 读取目标 LUT grid。
2. 用当前 engine 生成候选 LUT grid。
3. 优化当前参数，使候选 LUT 尽量拟合目标 LUT。
4. 分别评估：
   - 全 grid RGB RMSE / MAE
   - 中性轴 tone curve 误差
   - hue slice 响应误差
   - skin/sky/green patch 误差
   - clipping / monotonicity / smoothness
5. 记录每个 LUT 的最佳拟合误差和失败模式。

### 5.4 Go/No-Go 判断

| 结果 | 解释 | 下一步 |
|------|------|--------|
| 当前 engine 可拟合大多数 LUT | 主要瓶颈是优化器和 UI | 继续做 A4 optimizer |
| 只差 tone curve | 需要 1D 曲线或更强 shoulder/toe 模型 | 先扩 tone 模块 |
| hue/sat/lum 误差大 | 需要 6 色相/饱和/亮度控制 | 扩 HSL 正交参数 |
| 交叉通道误差大 | 当前 HSL 参数化不够 | 引入 3D residual LUT 或矩阵层 |
| 大面积 clipping/不可平滑 | 不能只靠参数拟合 baked LUT | 改为 prototype LUT + 可调强度 |

这个实验比直接做 AI image-to-LUT 更有诊断价值，因为它先回答“engine 能不能表达目标 look”。

---

## 六、对产品路线的启发

### 6.1 从“生成任意 LUT”改为“智能选择 + 微调”

更现实的 MVP 可以是：

```text
用户上传参考图
  -> AI 识别风格族：Fuji Classic Neg / Leica Classic / 2383 / ARRI 709 / ...
  -> 选择最接近 prototype
  -> 调整强度、曝光、白平衡、对比、饱和
  -> 输出 Panasonic V-Log .cube
```

这比承诺“任意参考图一键复刻”更可控，也更容易做出用户感知稳定的结果。

### 6.2 原型库可以同时服务两类用户

| 用户类型 | 入口 |
|----------|------|
| 不懂调色的用户 | 上传图，AI 选择 look |
| 懂调色的用户 | 直接选择 look 原型，再手调参数 |

这保留了当前项目“可解释配方”的优势，也吸收了 V-Log-Alchemy “成熟 look baked LUT”的优势。

### 6.3 参数化 engine 的定位应调整

当前 engine 不一定要承担完整风格表达。它可以承担：

- prototype 的强度控制
- 白平衡/曝光/对比/sat 的可解释微调
- 用户可分享的 recipe 层
- 对 prototype LUT 的轻量 residual 修正

而不是强行用 30-50 个参数重建所有官方相机色彩科学。

---

## 七、风险与注意事项

| 风险 | 说明 |
|------|------|
| 法务/授权 | V-Log-Alchemy 本仓库是 Apache 2.0，但其中“官方 LUT”来源和各品牌商标使用仍需单独谨慎核对，不能默认商业可用。 |
| 风格过硬 | 这些 LUT 很多是 baked look，可能出现贴边、强 clipping 或高饱和区域不自然。 |
| 机内 LUT 限制 | 33³ `.cube` 对复杂 log transform + creative grade 是折中方案，精度不如链式 DCTL/CST。 |
| 传感器差异 | README 也提醒 CFA 光谱响应不同，数学空间对齐不能完全复制另一台相机。 |
| 参数可解释性 | prototype LUT 本身是黑盒，需要额外设计“强度/微调/解释”层。 |

---

## 八、建议更新原报告

建议把 `2026-06-16-ai-image-to-lut-feasibility.md` 的结论改得更保守：

> 技术路线值得做原型；但 Go/No-Go 取决于真实 LUT/prototype 上的 engine 拟合能力，以及真实参考图上的跨内容泛化测试。优先做 Phase 0：用 V-Log-Alchemy 的开源 LUT 做表达能力 benchmark，再决定是否进入 4-6 周 MVP。

建议在路线图前新增 Phase 0：

- 建立 prototype registry，只记录来源、授权状态、接入策略和 benchmark 优先级。
- 用 V-Log-Alchemy 23 个 LUT 做 engine fitting benchmark。
- 产出失败模式分类：tone, hue, saturation, luminance, matrix, 3D residual。
- 选定 MVP 路线：
  - 参数化 engine 优先；
  - prototype LUT + 微调优先；
  - 或两者混合。

---

## 九、后续工作清单

- [ ] 写 `tools/fit_reference_lut.py`：拟合目标 `.cube` 到当前 engine 参数。
- [ ] 写 `tools/analyze_lut_response.py`：输出 neutral ramp、hue slice、patch table、clipping 统计。
- [ ] 为 V-Log-Alchemy LUT 生成一份 benchmark summary。
- [ ] 用 benchmark 结果更新 AI image-to-LUT 可行性报告。
- [ ] 评估 Apache 2.0 仓库之外的官方 LUT 来源和品牌命名风险。
