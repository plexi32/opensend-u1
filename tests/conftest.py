"""Minimal stand-in for OrcaSlicer's embedded `orca` module.

The real module only exists inside OrcaSlicer. This stub mirrors the few names the plugin
uses (see src/slic3r/plugin/PythonPluginBridge.cpp and pluginTypes/ in OrcaSlicer), so the
plugin can be imported and its capabilities exercised in plain pytest.
"""

import enum
import json
import sys
import types

orca = types.ModuleType("orca")
orca.registered = []


class base:
    def register_capabilities(self):
        pass


def plugin(cls):
    return cls


def register_capability(cls):
    orca.registered.append(cls)


class PluginResult(enum.Enum):
    Success = 0
    Skipped = 1
    RecoverableError = 2
    FatalError = 3


class ExecutionResult:
    def __init__(self, status=PluginResult.Success, message="", data=""):
        self.status, self.message, self.data = status, message, data

    @staticmethod
    def success(message="", data=""):
        return ExecutionResult(PluginResult.Success, message, data)

    @staticmethod
    def skipped(message=""):
        return ExecutionResult(PluginResult.Skipped, message)

    @staticmethod
    def failure(status, message, data=""):
        return ExecutionResult(status, message, data)


class _CapabilityBase:
    """Stored config is injected by tests via `_config`, like the host's per-capability store."""

    _config = "{}"

    def get_config(self):
        return self._config

    def save_config(self, config):
        self._config = config
        return True


slicing = types.ModuleType("orca.slicing")


class Step(enum.Enum):
    posSlice = 0
    psGCodePostProcess = 99


class SlicingPipelineCapabilityBase(_CapabilityBase):
    pass


slicing.Step = Step
slicing.SlicingPipelineCapabilityBase = SlicingPipelineCapabilityBase

orca.base = base
orca.plugin = plugin
orca.register_capability = register_capability
orca.PluginResult = PluginResult
orca.ExecutionResult = ExecutionResult
orca.slicing = slicing

sys.modules["orca"] = orca
sys.modules["orca.slicing"] = slicing


def make_config(**overrides) -> str:
    return json.dumps(overrides)
