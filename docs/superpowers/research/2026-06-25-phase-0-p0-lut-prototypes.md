# Phase 0: P0 LUT Prototype Baking

> 日期：2026-06-25  
> 目的：按 V-Log-Alchemy 的色彩逆向工程思路，将代表性非 Panasonic LUT 烘焙成 Panasonic V-Log/V-Gamut 可用 LUT。  
> 范围：V-Log-Alchemy 仅用于对照；源 LUT 从官方/公开入口临时取得或由用户自备，不把第三方源 LUT 放入仓库。

---

## 一、阶段原则

Phase 0 的目标是验证这条链路：

```text
Panasonic V-Log / V-Gamut
  -> 目标 LUT 期望的输入空间
  -> 应用目标 LUT
  -> bake 成 Panasonic V-Log .cube
  -> 用 samples/vlog.jpg 验证呈现效果
```

约束：

- 不新增 `external_luts/` 这类第三方资源目录。
- 不提交商业 LUT、授权不明 LUT、官网下载包或第三方源 LUT。
- V-Log-Alchemy 只作为 reference，对比最终呈现，不作为源 LUT。
- P0 中能公开取得且输入契约清楚的先烘焙；商业 LUT 先保留用户自备入口。

---

## 二、P0 原型短名单

| ID | 原型 | 源 LUT 输入契约 | 当前状态 |
|----|------|----------------|----------|
| `arri_classic_709_k1s1` | ARRI Alexa Classic 709 / K1S1 | ARRI LogC3 / AWG3 | 已退役：本地烘焙结果不如 V-Log-Alchemy 参考。 |
| `kodak_2383_pfe` | Kodak 2383 Print Film Emulation | Cineon Film Log / Rec.709 gamut | 已退役：本地烘焙结果不如 V-Log-Alchemy 参考。 |
| `visioncolor_osiris_m31` | VisionColor Osiris M31 | 视用户源 LUT 而定 | 商业/授权限制；后续用户自备源 LUT。 |
| `phantom_neutral` | Phantom Neutral / Phantom LUTs | 视用户源 LUT 而定 | 商业/授权限制；后续用户自备源 LUT。 |
| `emotive_color_alex` | Emotive Color Alex / GHAlex | 视用户源 LUT 而定 | 商业/授权限制；后续用户自备源 LUT。 |

---

## 三、实验结论

本轮曾临时实现 `tools/bake_target_lut_to_vlog.py`，用于验证
`V-Log/V-Gamut -> 目标 LUT 输入空间 -> 目标 LUT -> Panasonic V-Log .cube`
这条链路。

验证后结论是：这条方向技术上可行，但本地烘焙结果在 `samples/vlog.jpg`
上的呈现不如 V-Log-Alchemy 参考 LUT，尤其 Kodak/Cineon 路径仍需要更精确的
色彩空间和曲线契约。因此临时工具、测试和生成产物已从当前项目中移除，避免
把 P0 实验代码误认为可维护功能。

后续若继续走 P1/P2 官方 LUT 烘焙，应重新以 V-Log-Alchemy 的色彩空间链路为
reference 设计生产级工具，而不是沿用这次临时脚本。

---

## 四、后续任务

- [x] 清理错误的参数近似 P0 preset/LUT。
- [x] 实现临时 V-Log-Alchemy-style bake 工具，并在对比后移除。
- [x] 烘焙 ARRI Classic 709 和 Kodak 2383，并在与 V-Log-Alchemy 对比后移除本地生成 `.cube`。
- [x] 用 `samples/vlog.jpg` 导出验证图：
  - `output/vlog_Baked_ARRI_Classic709_VLog.jpg`（已移除）
  - `output/vlog_Baked_Kodak2383_VLog.jpg`（已移除）
  - `output/p0_baked_lut_comparison.jpg`（已移除）
- [x] 对照 V-Log-Alchemy 的 ARRI/Kodak 输出观察差异：ARRI 方向非常接近；Kodak 2383 方向接近，但当前 Cineon 映射比 V-Log-Alchemy 参考稍保守。
- [ ] 为 M31/Phantom/Emotive 设计用户自备源 LUT 的路径接入方式。
