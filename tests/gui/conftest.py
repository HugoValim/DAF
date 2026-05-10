import pytest


def pytest_collection_modifyitems(config, items):
    """Skip all GUI tests automatically."""
    for item in items:
        if "tests/gui/" in str(item.path):
            item.add_marker(pytest.mark.skip(reason="GUI tests temporarily skipped"))
