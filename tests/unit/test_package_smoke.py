from pff_fa_ai import __version__


def test_should_expose_package_version() -> None:
    assert __version__ == "0.1.0"
