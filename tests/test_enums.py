from pylutron_leap.api.enum import AreaMode


def test_default_enum():
    _val: AreaMode = AreaMode()
    print(_val)
    assert _val == AreaMode.Unknown


def test_valuesenum_to_string():
    _val: AreaMode = AreaMode()

    assert _val.name == "Unknown"


def test_valuesenum_values():
    _EXPECTED = ["Unknown", "DimLevel", "Switched"]
    _val = AreaMode.items()

    assert _val == _EXPECTED
