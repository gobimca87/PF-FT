from pf_ft_ai import __version__


def test_should_expose_package_version() -> None:
    assert __version__ == "0.1.0"
