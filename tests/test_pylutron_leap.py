from importlib.metadata import version


def test_version():
    assert version("pylutron_leap") == "0.1.0"
