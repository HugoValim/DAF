import sys
from unittest.mock import MagicMock


def test_epics_is_mock():
    import epics

    print(f"epics type: {type(epics).__name__}")
    print(f"epics.caget type: {type(epics.caget).__name__}")
    assert type(epics).__name__ == "MagicMock"
