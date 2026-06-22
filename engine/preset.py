"""
Film LUT Engine — Preset Loader
=================================
Scans the ``presets/`` directory, loads preset modules, validates them.
"""

import os
import importlib.util

# presets/ is at the project-root level (parent of engine/)
_ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
PRESETS_DIR = os.path.join(os.path.dirname(_ENGINE_DIR), 'presets')


def list_presets():
    """Return sorted list of available preset names (stem names of .py files
    in ``presets/``, excluding ``__init__``)."""
    names = []
    if not os.path.isdir(PRESETS_DIR):
        return names
    for fname in sorted(os.listdir(PRESETS_DIR)):
        if fname.endswith('.py') and fname != '__init__.py':
            names.append(fname[:-3])  # strip .py
    return names


def load_preset(name):
    """Load and validate a preset by name.

    Args:
        name: e.g. ``'5219'`` or ``'hassy_blue'``

    Returns:
        The ``PRESET`` dict from the corresponding ``presets/<name>.py``.

    Raises:
        FileNotFoundError – preset file doesn't exist.
        ValueError         – preset module doesn't export ``PRESET`` or is
                             structurally invalid.
    """
    # Try exact name first, then normalize hyphens ↔ underscores
    candidates = [name, name.replace('-', '_'), name.replace('_', '-')]
    preset_path = None
    for c in candidates:
        p = os.path.join(PRESETS_DIR, f'{c}.py')
        if os.path.exists(p):
            preset_path = p
            break
    if preset_path is None:
        available = list_presets()
        hint = f" Available: {', '.join(available)}" if available else ''
        raise FileNotFoundError(
            f"Preset '{name}' not found in {PRESETS_DIR}.{hint}"
        )

    spec = importlib.util.spec_from_file_location(name, preset_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, 'PRESET'):
        raise ValueError(f"Preset '{name}' does not export a PRESET dict")

    preset = module.PRESET
    _validate(preset, name)
    return preset


def _validate(preset, name):
    """Validate preset structure. Raises ValueError on failure."""
    required = ['name', 'title', 'lut_name', 'tone', 'color']
    for key in required:
        if key not in preset:
            raise ValueError(f"Preset '{name}' missing key: '{key}'")

    tone_keys = [
        'black_lift', 'shadow_toe_pivot', 'shadow_toe_power',
        'contrast', 'highlight_shoulder_start', 'highlight_shoulder_power',
        'per_channel_contrast',
    ]
    for key in tone_keys:
        if key not in preset['tone']:
            raise ValueError(f"Preset '{name}' missing tone key: '{key}'")
    if len(preset['tone']['per_channel_contrast']) != 3:
        raise ValueError(
            f"Preset '{name}': per_channel_contrast must have 3 elements"
        )

    color_keys = [
        'shadow_tint', 'highlight_tint', 'global_saturation',
        'highlight_desat_start', 'highlight_desat_max',
        'skin_hue_min', 'skin_hue_max', 'skin_sat_adjust',
        'teal_push', 'orange_push',
    ]
    for key in color_keys:
        if key not in preset['color']:
            raise ValueError(f"Preset '{name}' missing color key: '{key}'")
    if len(preset['color']['shadow_tint']) != 3:
        raise ValueError(f"Preset '{name}': shadow_tint must have 3 elements")
    if len(preset['color']['highlight_tint']) != 3:
        raise ValueError(
            f"Preset '{name}': highlight_tint must have 3 elements"
        )
