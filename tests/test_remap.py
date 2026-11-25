import pytest

from opensend_u1.remap import is_identity, parse_mapping, remap_file, remap_line

SWAP = {0: 1, 1: 0}


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("T0\n", "T1\n"),
        ("  T1 ; switch\n", "  T0 ; switch\n"),
        ("M104 S210 T0\n", "M104 S210 T1\n"),
        ("M109 S220 T1 ; wait\n", "M109 S220 T0 ; wait\n"),
        ("T3\n", "T3\n"),  # unmapped tools stay as they are
        ("; T0 in a comment\n", "; T0 in a comment\n"),
        ("G1 X10 Y10\n", "G1 X10 Y10\n"),
        ("M140 S60 T0\n", "M140 S60 T0\n"),  # bed temperature: no tool parameter semantics
    ],
)
def test_remap_line(line, expected):
    assert remap_line(line, SWAP) == expected


def test_remap_file_keeps_line_endings(tmp_path):
    gcode = tmp_path / "plate.gcode"
    gcode.write_bytes(b"T0\r\nG1 X1\r\nT1\r\n")

    assert remap_file(gcode, SWAP) == 2
    assert gcode.read_bytes() == b"T1\r\nG1 X1\r\nT0\r\n"


def test_parse_mapping_accepts_json_string_keys():
    assert parse_mapping({"0": 2, "1": 3}, toolhead_count=4) == {0: 2, 1: 3}


def test_parse_mapping_rejects_out_of_range_toolhead():
    with pytest.raises(ValueError, match="outside"):
        parse_mapping({"0": 4}, toolhead_count=4)


def test_parse_mapping_rejects_shared_toolhead():
    with pytest.raises(ValueError, match="same toolhead"):
        parse_mapping({"0": 1, "1": 1}, toolhead_count=4)


def test_is_identity():
    assert is_identity({0: 0, 1: 1})
    assert not is_identity(SWAP)
