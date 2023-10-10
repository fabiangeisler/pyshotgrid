import sys

import pytest
import importlib


def test_import_error(use_tank_vendor):
    if use_tank_vendor:
        with pytest.raises(ImportError):
            import shotgun_api3
    else:
        import shotgun_api3

    import pyshotgrid
