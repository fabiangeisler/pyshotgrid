import importlib


def test_import_against_sgtk_vendored_shotgun_api3(use_shotgun_api3_from_sgtk):
    import pyshotgrid

    importlib.reload(pyshotgrid.core)
    importlib.reload(pyshotgrid.sg_default_entities)
    importlib.reload(pyshotgrid)
