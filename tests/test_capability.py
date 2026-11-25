import orca
from conftest import make_config

import opensend_u1
from opensend_u1.capability import ToolheadMapping


class Ctx:
    def __init__(self, step, gcode_path=""):
        self.step = step
        self.gcode_path = gcode_path


def capability(**config):
    cap = ToolheadMapping()
    cap._config = make_config(**config)
    return cap


def test_package_registers_the_capability():
    orca.registered.clear()
    opensend_u1.OpenSendU1().register_capabilities()
    assert orca.registered == [ToolheadMapping]


def test_name_is_safe_for_preset_strings():
    assert ";" not in ToolheadMapping().get_name()


def test_ignores_geometry_steps():
    result = capability().execute(Ctx(orca.slicing.Step.posSlice))
    assert result.status == orca.PluginResult.Success


def test_default_config_is_identity_and_skips():
    result = capability().execute(Ctx(orca.slicing.Step.psGCodePostProcess))
    assert result.status == orca.PluginResult.Skipped


def test_remaps_exported_gcode(tmp_path):
    gcode = tmp_path / "plate.gcode"
    gcode.write_text("T0\nG1 X1\nT1\n")

    cap = capability(mapping={"0": 2, "1": 3})
    result = cap.execute(Ctx(orca.slicing.Step.psGCodePostProcess, str(gcode)))

    assert result.status == orca.PluginResult.Success
    assert gcode.read_text() == "T2\nG1 X1\nT3\n"


def test_invalid_mapping_fails_the_export(tmp_path):
    gcode = tmp_path / "plate.gcode"
    gcode.write_text("T0\n")

    cap = capability(mapping={"0": 1, "1": 1})
    result = cap.execute(Ctx(orca.slicing.Step.psGCodePostProcess, str(gcode)))

    assert result.status == orca.PluginResult.FatalError
    assert gcode.read_text() == "T0\n"
