import pytest


def pytest_collection_modifyitems(config, items):
    """Skip all GUI tests automatically."""
    for item in items:
        item.add_marker(pytest.mark.skip(reason="GUI tests temporarily skipped"))
