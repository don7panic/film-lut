# CLI 精简为「生成 LUT」+「套用 LUT」

**日期**：2026-06-22
**状态**：已确认，待实现
**允许破坏性变更**：是（项目处于开发阶段）

## 背景

当前 [lutex.py](../../lutex.py) 把"生成 LUT"和"套用 LUT"耦合在 `--apply` 模式里：必须带 `--preset` 现场重算 LUT 再套用，还要用 `--apply-type vlog|standard` 区分输入类型。用户手上已有的 `.cube` 文件无法直接复用——这正是项目的核心使用场景（生成一次，多次套用查看效果）。

`engine/apply.py` 也反映了这种耦合：`apply_lut_to_file` 同时承担"生成 LUT + 套用"两个职责，还混入了 `generate_test_image` 等参考图生成逻辑。

## 目标

项目只需两个核心功能：

1. **生成 LUT**：按 preset 生成 `.cube` 写入磁盘
2. **套用 LUT**：读取用户提供的 `.cube`，套用到图片查看效果

## 目标 CLI

```bash
# 功能 1：生成 LUT（写入 luts/）
uv run python lutex.py --preset 5219
uv run python lutex.py --preset 5219 --size 65
uv run python lutex.py --preset 5219 --output /path/to/luts

# 功能 2：套用 LUT 看效果（输出 output/）
uv run python lutex.py --apply-cube luts/Ricoh_positive.cube samples/vlog.jpg
uv run python lutex.py --apply-cube luts/Ricoh_positive.cube samples/vlog.jpg --apply-output out.jpg

# 辅助
uv run python lutex.py --list
```

## 参数变更

| 参数 | 状态 | 说明 |
|------|------|------|
| `--preset` | 保留，仅生成模式必需 | 生成哪个胶片风格 |
| `--apply-cube <CUBE> <IMAGE>` | **新增** | `.cube` 路径 + 图片路径，套用模式 |
| `--apply-output` | 保留 | 套用模式输出路径（可选） |
| `--list` | 保留 | 列出可用 preset |
| `--size` | 保留 | 生成模式 grid size |
| `--output` | 保留 | 生成模式 LUT 输出目录 |
| `--apply` | **移除** | 被 `--apply-cube` 取代 |
| `--apply-type` | **移除** | `.cube` 已含完整变换，无需区分输入 |
| `--preview` | **移除** | 合成色卡参考图，非核心 |

## 行为规则

1. `--apply-cube <CUBE> <IMAGE>`：读 `.cube` → 三线性插值套用 → 存盘。**不解释输入**（`.cube` 已含完整色彩变换，含 V-Log 反 log）。
2. `--apply-cube` 与 `--preset` 互斥（两者代表两种模式，不应同传）。
3. `--apply-cube` 模式：`--apply-output` 可选；省略时输出 `output/<原图名>_<cube文件名>.jpg`（cube 文件名去扩展名）。
4. `--apply-cube` 模式忽略 `--size`（LUT 分辨率由 `.cube` 文件决定）。
5. 无任何主参数时打印 usage 并退出。

## 实现变更

### `engine/apply.py` — 重写为单职责模块

移除全部旧函数：`apply_lut_to_file`、`generate_test_image`、`_test_strip`、`_hue_wheel`。

新增唯一函数：

```python
def apply_cube_file(cube_path, image_path, output_path):
    """读 .cube 文件，套用到图片，保存结果。

    Args:
        cube_path:  .cube 文件路径
        image_path: 输入图片路径
        output_path: 输出图片路径
    """
    # 复用 lut3d.load_cube_file + apply_lut_to_image
    # Pillow 加载/保存（与原实现一致：exif_transpose、convert RGB、quality 95）
```

### `lutex.py` — CLI 重写

- argparse 调整：新增 `--apply-cube`（接收两个值：cube 路径、图片路径），移除 `--apply` / `--apply-type` / `--preview`
- `--apply-cube` 与 `--preset` 互斥校验
- 新增 apply-cube 分支：调用 `engine.apply.apply_cube_file`
- 移除对 `engine.apply` 旧函数的导入
- 顶部 docstring 用法示例同步更新

### `tools/c200_final_calibration.py` — 内联辅助函数

该脚本原从 `engine.apply` 导入 `_test_strip` / `_hue_wheel`。重写 `engine/apply.py` 后这些函数消失。处理方式：在脚本内**内联**这两个函数的完整实现，移除 `from engine.apply import` 行，保持脚本自洽可跑。不改脚本其他逻辑。

## 不在范围内

- 不改色彩管线（`engine/core.py`）
- 不改 LUT 生成逻辑（`engine/lut3d.py`）
- 不改 preset 定义（`presets/`）
- 不改 `.cube` 文件格式
- 不删 `tools/` 下其他脚本

## 测试

### 自动测试

现有 `tests/test_vlog_and_cube.py` 测的是 `engine.core` 和 `engine.lut3d`，不涉及 `engine.apply`，不受影响，应继续通过。

### 手动验证

两条主命令：

```bash
# 套用 LUT
uv run python lutex.py --apply-cube luts/Ricoh_positive.cube samples/vlog.jpg
# 预期：output/vlog_Ricoh_positive.jpg

# 生成 LUT
uv run python lutex.py --preset 5219
# 预期：luts/S9_VLog_to_5219.cube + S9_Standard_to_5219.cube
```

### 连带验证

```bash
# calibration 脚本仍可跑（内联后不依赖 engine.apply）
uv run python tools/c200_final_calibration.py
```
