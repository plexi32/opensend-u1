"""Slicing-pipeline capability that rewrites tool numbers in the exported G-code.

The capability runs at every slicing step but only acts at Step.psGCodePostProcess,
where ctx.gcode_path points at the exported G-code that may be edited in place.
It runs on the slicing worker thread: never call orca.host.ui.* from here.
"""

import json

import orca

from .remap import is_identity, parse_mapping, remap_file

DEFAULT_TOOLHEADS = 4  # Snapmaker U1


class ToolheadMapping(orca.slicing.SlicingPipelineCapabilityBase):
    def get_name(self):
        # Shown in the preset's "Slicing Pipeline Plugin" picker. Must not contain ';'.
        return "OpenSend Toolhead Mapping"

    def get_default_config(self):
        return {
            "enabled": True,
            "toolhead_count": DEFAULT_TOOLHEADS,
            # filament index (as string, JSON keys are strings) -> toolhead index
            "mapping": {str(i): i for i in range(DEFAULT_TOOLHEADS)},
        }

    def execute(self, ctx):
        if ctx.step != orca.slicing.Step.psGCodePostProcess:
            return orca.ExecutionResult.success()

        config = {**self.get_default_config(), **json.loads(self.get_config())}
        if not config["enabled"]:
            return orca.ExecutionResult.skipped("disabled in plugin config")

        try:
            mapping = parse_mapping(config["mapping"], int(config["toolhead_count"]))
        except (ValueError, TypeError) as e:
            return orca.ExecutionResult.failure(orca.PluginResult.FatalError, f"Invalid toolhead mapping: {e}")

        if is_identity(mapping):
            return orca.ExecutionResult.skipped("identity mapping, nothing to do")

        changed = remap_file(ctx.gcode_path, mapping)
        return orca.ExecutionResult.success(f"remapped {changed} G-code lines")
