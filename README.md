# OpenSend U1

Open-source OrcaSlicer plugin for the Snapmaker U1. It maps the filaments of a print to the
printer's toolheads by rewriting the tool numbers (`T0`–`T3`, and `T` parameters of
`M104`/`M109`/`M568`) in the exported G-code.

## Install

1. Download the latest `opensend_u1-*.whl` from the [Releases](https://github.com/plexi32/opensend-u1/releases) page.
2. In OrcaSlicer, open the **Plugins** dialog and install the wheel.
3. In your process preset, add **OpenSend Toolhead Mapping** under *Slicing Pipeline Plugin*.
4. Edit the mapping in the plugin's **Config** tab, for example to print filament 1 on toolhead 3:

   ```json
   { "enabled": true, "toolhead_count": 4, "mapping": { "0": 0, "1": 3, "2": 2, "3": 1 } }
   ```

The mapping is applied when the G-code is exported or uploaded. The G-code preview inside
OrcaSlicer still shows the original tool numbers.

## Develop

```sh
python -m venv .venv
.venv/Scripts/activate        # Windows; use .venv/bin/activate elsewhere
pip install -e ".[dev]"
pytest
python -m build --wheel       # -> dist/opensend_u1-<version>-py3-none-any.whl
```

`tests/conftest.py` provides a stub of the `orca` module, which only exists inside OrcaSlicer.
Keep logic that does not need OrcaSlicer (like `remap.py`) free of `orca` imports so it stays
testable.

### Layout

| Path | Purpose |
| --- | --- |
| `src/opensend_u1/__init__.py` | `@orca.plugin` package class, registers the capabilities |
| `src/opensend_u1/capability.py` | Slicing-pipeline capability, acts at `Step.psGCodePostProcess` |
| `src/opensend_u1/remap.py` | Pure G-code remapping logic |
| `tests/` | pytest suite with an `orca` stub |

### Release

Bump `version` in `pyproject.toml`, commit, then tag and push:

```sh
git tag v0.2.0 && git push origin v0.2.0
```

The release workflow tests, builds the wheel and attaches it to a GitHub release.

## Roadmap

- A `Pages` capability with a dialog that shows the plate's filaments and lets you pick the toolhead
  for each, instead of editing JSON.
- Direct upload to the U1 over its Moonraker HTTP API.

## License

AGPL-3.0-or-later, the same license as OrcaSlicer.
